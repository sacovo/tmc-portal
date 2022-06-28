from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse

from django_drf_filepond.api import delete_stored_upload, get_stored_upload_file_data, get_stored_upload, store_upload

from tmc.forms import DocumentForm, LoginForm, SignupForm
from tmc.models import Inscription, Recording, RequiredRecording
from tmc.services import all_fields, fetch_inscription, process_signup, process_update, send_auth_message

# Create your views here.


def landing(request):
    if not request.user.is_authenticated:
        return redirect('tmc:signup')
    instance = Inscription.objects.filter(user=request.user).first()

    if instance is None and request.user.is_staff:
        return redirect('admin:index')
    if instance is not None:
        return redirect('tmc:inscription_detail', pk=instance.pk)
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

    store_upload(upload_id, path)
    name, upload = get_stored_upload_file_data(get_stored_upload(upload_id))

    recording.recording.save(name, ContentFile(upload))
    recording.save()
    delete_stored_upload(upload_id, delete_file=True)
    return HttpResponse(recording.recording.url)


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
