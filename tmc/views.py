from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from django.db import transaction
from django.forms import inlineformset_factory
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django_drf_filepond.api import (
    delete_stored_upload,
    get_stored_upload,
    get_stored_upload_file_data,
    store_upload,
)
from django_q.tasks import async_task

from tmc.forms import (
    DocumentForm,
    HelperForm,
    HostForm,
    JuryForm,
    LoginForm,
    SignupForm,
    SlotFormsetHelper,
)
from tmc.models import Helper, Recording, RequiredRecording, TimeSlot
from tmc.services import (
    all_fields,
    fetch_helper,
    fetch_host,
    fetch_inscription,
    fetch_jury,
    process_helper_signup,
    process_host_signup,
    process_jury_signup,
    process_signup,
    process_update,
    send_auth_message,
)

# Create your views here.


def landing(request):
    if not request.user.is_authenticated:
        return redirect('tmc:signup')

    if request.user.is_staff:
        return redirect('admin:index')

    user = request.user

    if hasattr(user, 'inscription'):
        return redirect('tmc:inscription_detail', pk=user.inscription.pk)

    if hasattr(user, 'hostfamily'):
        return redirect('tmc:host_detail', pk=user.hostfamily.pk)

    if hasattr(user, 'helper'):
        return redirect('tmc:helper_detail', pk=user.helper.pk)

    if hasattr(user, 'jury'):
        return redirect('tmc:jury_detail', pk=user.jury.pk)

    return redirect('tmc:signup')


def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            send_auth_message(
                form.cleaned_data['email'],
                request.build_absolute_uri(reverse('tmc:landing')),
            )
            return render(request, 'tmc/login_sent.html', {'form': form})
    return render(request, 'tmc/login.html', {'form': form})


@login_required
def view_signup(request, pk):
    instance = fetch_inscription(pk, request.user)

    return render(request, 'tmc/inscription_detail.html', {
        'instance': instance,
        'fields': all_fields(instance)
    })


@login_required
def update_signup(request, pk):
    instance = fetch_inscription(pk, request.user)

    form = SignupForm(instance=instance)

    if request.method == 'POST':
        form = SignupForm(request.POST, instance=instance)

        if form.is_valid():
            process_update(form)
            return redirect('tmc:inscription_detail', pk=instance.pk)
    return render(request, 'tmc/inscription_update.html', {'form': form, 'instance': instance})


@login_required
def update_documents(request, pk):
    instance = fetch_inscription(pk, request.user)

    form = DocumentForm(instance=instance)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save()
            return redirect('tmc:documents', pk=instance.pk)

    return render(
        request,
        'tmc/inscription_documents.html',
        {
            'form': form,
            'instance': instance
        },
    )


@login_required
def recordings(request, pk):
    instance = fetch_inscription(pk, request.user)

    requirements = []

    for requirement in RequiredRecording.objects.filter(instrument=instance.instrument):
        requirement.recording = Recording.objects.filter(requirement=requirement,
                                                         uploader=instance).first()
        requirements.append(requirement)

    return render(request, 'tmc/recordings.html', {
        'requirements': requirements,
        'instance': instance
    })



@login_required
def upload_recording(request, inscription_pk, requirement_pk):
    requirement = get_object_or_404(RequiredRecording, pk=requirement_pk)
    instance = fetch_inscription(inscription_pk, request.user)

    recording, _ = Recording.objects.get_or_create(uploader=instance, requirement=requirement)

    extension = request.POST['extension']
    upload_id = request.POST['upload_id']
    path = f"{requirement.nr:02}_{requirement.slug}_{upload_id}.{extension}"

    async_task(store_uploaded_recording, upload_id, path, recording)

    return HttpResponse('ok')

def store_uploaded_recording(upload_id, path, recording):
    store_upload(upload_id, path)
    name, upload = get_stored_upload_file_data(get_stored_upload(upload_id))

    recording.recording.save(name, ContentFile(upload))
    recording.is_complete = True
    recording.save()
    delete_stored_upload(upload_id, delete_file=True)


def signup(request):
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                instance = process_signup(form, request.build_absolute_uri(reverse('tmc:landing')))
                login(request, instance.user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect('tmc:inscription_detail', pk=instance.pk)

    return render(request, 'tmc/signup.html', {'form': form})


def host_signup(request):
    form = HostForm()

    if request.method == 'POST':
        form = HostForm(request.POST)

        if form.is_valid():
            instance = process_host_signup(form, request)
            login(request, instance.user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect('tmc:host_detail', pk=instance.pk)

    return render(request, 'tmc/host_form.html', {'form': form})


@login_required
def view_host(request, pk):
    host = fetch_host(pk, request.user)
    form = HostForm(instance=host)

    message = ''

    if request.method == 'POST':
        form = HostForm(request.POST, instance=host)

        if form.is_valid():
            form.save()
            message = _("Your information was updated")

    return render(
        request,
        'tmc/host_form.html',
        {
            'host': host,
            'form': form,
            'message': message,
        },
    )


SlotFormset = inlineformset_factory(Helper, TimeSlot, fields=['date', 'slot'], extra=3, max_num=4)


def helper_signup(request):
    form = HelperForm()
    formset = SlotFormset()
    helper = SlotFormsetHelper()

    if request.method == 'POST':
        form = HelperForm(request.POST)
        formset = SlotFormset(request.POST)

        if form.is_valid() and formset.is_valid():
            instance = process_helper_signup(form, formset, request)
            login(request, instance.user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect('tmc:helper_detail', pk=instance.pk)

    return render(request, 'tmc/helper_form.html', {
        'form': form,
        'formset': formset,
        'formset_helper': helper,
    })


@login_required
def view_helper(request, pk):
    helper = fetch_helper(pk, request.user)
    form = HelperForm(instance=helper)
    formset = SlotFormset(instance=helper)
    formset_helper = SlotFormsetHelper()

    message = ''

    if request.method == 'POST':
        form = HelperForm(request.POST, instance=helper)
        formset = SlotFormset(request.POST, instance=helper)

        if form.is_valid() and formset.is_valid():
            print(request.POST)
            form.save()
            formset.save()

            return redirect('tmc:helper_detail', pk=pk)

    return render(
        request,
        'tmc/helper_form.html',
        {
            'helper': helper,
            'form': form,
            'formset': formset,
            'formset_helper': formset_helper,
            'message': message,
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def jury_signup(request):
    form = JuryForm()

    if request.method == 'POST':
        form = JuryForm(request.POST)
        if form.is_valid():
            instance = process_jury_signup(form, request)
            return redirect('tmc:jury_detail', pk=instance.pk)
    return render(request, 'tmc/jury_form.html', {'form': form})


@login_required
def view_jury(request, pk):
    jury = fetch_jury(pk, request.user)
    form = JuryForm(instance=jury)

    message = ''

    if request.method == 'POST':
        form = JuryForm(request.POST, instance=jury)

        if form.is_valid():
            form.save()
            message = _("Your information was updated")

    return render(
        request,
        'tmc/jury_form.html',
        {
            'jury': jury,
            'form': form,
            'message': message,
        },
    )
