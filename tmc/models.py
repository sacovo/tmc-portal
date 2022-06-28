import secrets
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from uuid import uuid4

from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from address.models import AddressField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
MALE = 'm'
FEMALE = 'f'
NONBINARY = 'n'
DONT_KNOW = 'x'

GENDER_CHOICES = (
    (FEMALE, _("Female")),
    (MALE, _("Male")),
    (NONBINARY, _("Non-Binary")),
    (DONT_KNOW, _("Don't know")),
)

LANGUAGE_OF_CORRESPONDENCES = (
    ('en', _("English")),
    ('de', _("German")),
)


class Language(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instrument(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class JuryMember(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    instrument = models.ForeignKey(Instrument, models.CASCADE)

    is_pre = models.BooleanField()


class Correpetitor(models.Model):
    pass


class RequiredRecording(models.Model):
    name = models.CharField(max_length=600)
    slug = models.SlugField()
    nr = models.IntegerField()
    instrument = models.ForeignKey(Instrument, models.CASCADE)

    def __str__(self):
        return self.name


def recording_path(instance, filename):
    uploader = instance.uploader
    return f'{uploader.uid}/recordings/{filename}'


class Recording(models.Model):
    requirement = models.ForeignKey(RequiredRecording, models.CASCADE)
    recording = models.FileField(
        upload_to=recording_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            'mp4',
            'avi',
            'mov',
            'mkv',
        ])],
    )
    uploader = models.ForeignKey("Inscription", models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.recording.name.rsplit('/')[-1]


def generate_secret_id():
    return secrets.token_hex(4)


class Inscription(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    secret_id = models.CharField(max_length=8, default=generate_secret_id, unique=True)
    instrument = models.ForeignKey(Instrument, models.CASCADE, verbose_name=_("instrument"))

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name=_("gender"))
    given_name = models.CharField(max_length=120, verbose_name=_("given name"))
    surname = models.CharField(max_length=120, verbose_name=_("surname"))

    date_of_birth = models.DateField(verbose_name=_("date of birth"))

    nationality = CountryField(verbose_name=_("nationality"))

    address = AddressField(verbose_name=_("address"))

    mother_tongue = models.CharField(max_length=120, verbose_name=_("language"))
    language_of_correspondence = models.CharField(
        max_length=120,
        choices=LANGUAGE_OF_CORRESPONDENCES,
        verbose_name=_("language of correspondence"),
    )

    phone = PhoneNumberField(
        verbose_name=_("phone"),
        help_text=_("please remember to add your country prefix"),
    )
    email = models.EmailField(
        verbose_name=_("e-mail"),
        unique=True,
        error_messages={'unique': _("This email has already been registered.")},
        help_text=_(
            "make sure your e-mail is correct, as all communication will be done over e-mail"))

    education = models.TextField(max_length=500, verbose_name=_("education"))
    occupation = models.CharField(max_length=60, verbose_name=_("occupation"))
    notes = models.TextField(
        blank=True,
        verbose_name=_("notes"),
        help_text=_(
            "any information that we should know beforhand, not mentioned otherwise in this form"),
    )

    emergency_contact = models.CharField(
        max_length=120,
        verbose_name=_("emergency contact"),
        help_text=_("name of your emergency contact"),
    )
    emergency_phone = PhoneNumberField(
        verbose_name=_("emergency phone"),
        help_text=_("phone number of your emergency contact"),
    )
    emergency_relation = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("emergency relation"),
        help_text=_("how are you related to your emergency contact, (family, friends, ...)"),
    )

    accomodation_needed = models.BooleanField(
        verbose_name=_("accomodation needed"),
        help_text=_("do you need us to organise accomodation?"))
    is_smoker = models.BooleanField(verbose_name=_("smoker"))
    food_needed = models.BooleanField(verbose_name=_("need food"))
    vegetarian = models.BooleanField(verbose_name=_("vegetarian"))

    allergies = models.CharField(max_length=120, blank=True, verbose_name=_("allergies"))

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("submitted"))

    host_family = models.ForeignKey(
        "HostFamily",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    passport = models.FileField(blank=True, upload_to='documents/')
    photo = models.ImageField(blank=True, upload_to='photos/')

    def uploaded_recordings(self):
        return Recording.objects.filter(uploader=self).count()

    def total_recordings(self):
        return RequiredRecording.objects.filter(instrument=self.instrument).count()

    def __str__(self):
        return f'{self.given_name} {self.surname}'

    def todos(self):
        todos = []

        if self.uploaded_recordings() < self.total_recordings():
            todos.append(_("Upload required recordings"))
        print(self.passport)
        if not self.passport:
            todos.append(_("Upload scan of your passport"))
        if not self.photo:
            todos.append(_("Upload a photo of yourself"))

        return todos

    def get_absolute_url(self):
        return reverse('tmc:inscription_detail', kwargs=dict(pk=self.pk))


class HostFamily(models.Model):
    given_name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    address = AddressField()

    phone = PhoneNumberField()
    mobile = PhoneNumberField()

    email = models.EmailField()

    single_rooms = models.PositiveSmallIntegerField()
    double_rooms = models.PositiveSmallIntegerField()

    provides_breakfast = models.BooleanField()

    has_own_bathroom = models.BooleanField()
    has_wifi = models.BooleanField()
    provides_transport = models.BooleanField()

    preferred_gender = models.CharField(max_length=5, choices=GENDER_CHOICES, blank=True)

    languages = models.ManyToManyField(Language)

    pets = models.CharField(blank=True, max_length=180)
    practice_allowed = models.BooleanField()
    practice_notes = models.CharField(blank=True, max_length=180)

    smoking_allowed = models.BooleanField()
    notes = models.TextField(blank=True)

    submitted_at = models.DateTimeField()

    def __str__(self):
        return f'{self.given_name} {self.surname}'
