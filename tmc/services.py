from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, reverse

from sesame.utils import get_query_string
from django.conf import settings
from constance import config
from django.core.mail import message, send_mail

from tmc.models import Helper, HostFamily, Inscription, JuryMember, TimeSlot

EXCLUDED_FIELDS = [
    'secret_id', 'internal_note', 'host_family', 'user', 'passport', 'photo', 'recording',
    'has_recordings', 'has_documents', 'payment', 'payment_date', 'is_qualified', 'selection'
]


def all_fields(instance):
    for field in instance._meta.get_fields():

        if field.name in EXCLUDED_FIELDS:
            continue

        yield {'field': field, 'value': getattr(instance, field.name)}


def fetch_inscription(pk, user):

    instance = get_object_or_404(Inscription, uid=pk)

    if instance.user.pk != user.pk and not user.is_staff:
        raise PermissionDenied()
    return instance


def fetch_host(pk, user):
    host = get_object_or_404(HostFamily, pk=pk)

    if host.user.pk != user.pk and not user.is_staff:
        raise PermissionDenied()

    return host


def fetch_jury(pk, user):
    jury = get_object_or_404(JuryMember, pk=pk)

    if jury.user.pk != user.pk and not user.is_staff:
        raise PermissionDenied()

    return jury


def fetch_helper(pk, user):
    helper = get_object_or_404(Helper, pk=pk)

    if helper.user.pk != user.pk and not user.is_staff:
        raise PermissionDenied()

    return helper


def create_user(inscription):

    user = get_user_model().objects.create(
        username=inscription.email,
        email=inscription.email,
        first_name=inscription.given_name,
        last_name=inscription.surname,
    )
    inscription.user = user
    inscription.save()

    return user


@transaction.atomic
def process_signup(form, target_url):
    inscription: Inscription = form.save(commit=False)
    create_user(inscription)
    send_signup_message(inscription, target_url)
    return inscription


@transaction.atomic
def process_helper_signup(form, formset, request):
    helper: Helper = form.save(commit=False)
    create_user(helper)

    formset.instance = helper
    formset.save()

    target_url = request.build_absolute_uri(reverse('tmc:helper_detail', args=(helper.pk, )))
    send_helper_signup(helper, target_url)

    return helper


@transaction.atomic
def process_host_signup(form, request):
    host: HostFamily = form.save(commit=False)
    create_user(host)

    target_url = request.build_absolute_uri(reverse('tmc:host_detail', args=(host.pk, )))

    send_host_signup(host, target_url)

    return host


@transaction.atomic
def process_jury_signup(form, request):
    jury: JuryMember = form.save(commit=False)
    create_user(jury)

    target_url = request.build_absolute_uri(reverse('tmc:jury_detail', args=(jury.pk, )))

    send_jury_signup(jury, target_url)

    return jury


@transaction.atomic
def process_update(form):
    form.save(commit=True)


def send_message(subject_template, text_template, inscription=None, user=None, target_url=''):

    if user is None:
        user = inscription.user

    format_dict = {
        'inscription': inscription or user,
        'auth_link': target_url + get_query_string(user),
    }
    subject = subject_template.format(**format_dict)

    message = text_template.format(**format_dict)

    email = inscription.email if inscription is not None else user.email

    send_mail(
        subject,
        message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


def send_signup_message(inscription: Inscription, target_url):
    send_message(config.WELCOME_SUBJECT, config.WELCOME_TEXT, inscription, target_url=target_url)


def send_auth_message(inscription: Inscription, target_url):
    send_message(config.AUTH_SUBJECT, config.AUTH_TEXT, None, inscription, target_url=target_url)


def send_host_signup(host, target_url):
    send_message(config.HOST_SIGNUP_SUBJECT, config.HOST_SIGNUP_TEXT, host, target_url=target_url)


def send_helper_signup(helper, target_url):
    send_message(config.HELPER_SIGNUP_SUBJECT,
                 config.HELPER_SIGNUP_TEXT,
                 helper,
                 target_url=target_url)


def send_jury_signup(jury, target_url):
    send_message(config.JURY_SIGNUP_SUBJECT, config.JURY_SIGNUP_TEXT, jury, target_url=target_url)
