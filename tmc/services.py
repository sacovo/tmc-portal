from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

from sesame.utils import get_query_string
from django.conf import settings
from constance import config
from django.core.mail import message, send_mail

from tmc.models import Inscription

EXCLUDED_FIELDS = ['secret_id', 'host_family', 'user', 'passport', 'photo', 'recording']


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


@transaction.atomic
def process_signup(form, target_url):
    inscription: Inscription = form.save(commit=False)
    user = get_user_model().objects.create(
        username=inscription.email,
        email=inscription.email,
        first_name=inscription.given_name,
        last_name=inscription.surname,
    )
    inscription.user = user
    inscription.save()

    send_signup_message(inscription, target_url)

    return inscription


@transaction.atomic
def process_update(form):
    form.save(commit=True)


def send_message(subject_template, text_template, inscription, target_url):
    format_dict = {
        'inscription': inscription,
        'auth_link': target_url + get_query_string(inscription.user),
    }
    subject = subject_template.format(**format_dict)

    message = text_template.format(**format_dict)

    send_mail(subject,
              message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[inscription.email])


def send_signup_message(inscription: Inscription, target_url):
    send_message(config.WELCOME_SUBJECT, config.WELCOME_TEXT, inscription, target_url)


def send_auth_message(inscription: Inscription, target_url):
    send_message(config.AUTH_SUBJECT, config.AUTH_TEXT, inscription, target_url)
