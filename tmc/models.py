import secrets
from uuid import uuid4

from address.models import AddressField
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
MALE = "m"
FEMALE = "f"
NONBINARY = "n"
DONT_KNOW = "x"

GENDER_CHOICES = (
    (FEMALE, _("Female")),
    (MALE, _("Male")),
    (NONBINARY, _("Non-Binary")),
    (DONT_KNOW, _("Don't know")),
)

LANGUAGE_OF_CORRESPONDENCES = (
    ("en", _("English")),
    ("de", _("German")),
)


class Language(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instrument(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PersonBase(models.Model):
    class Meta:
        abstract = True

    given_name = models.CharField(max_length=120, verbose_name=_("given name"))
    surname = models.CharField(max_length=120, verbose_name=_("surname"))

    address = AddressField(verbose_name=_("address"), null=True, blank=True)
    phone = PhoneNumberField(
        verbose_name=_("phone"),
        help_text=_("please remember to add your country prefix"),
    )
    email = models.EmailField(
        verbose_name=_("e-mail"),
        unique=True,
        error_messages={"unique": _("This email has already been registered.")},
        help_text=_(
            "make sure your e-mail is correct, as all communication will be done over e-mail"
        ),
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("submitted"))

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.given_name} {self.surname}"


class JuryMember(PersonBase):
    instrument = models.ForeignKey(
        Instrument, models.CASCADE, verbose_name=_("instrument")
    )
    kind = models.CharField(max_length=120, verbose_name=_("function TMC"), blank=True)

    date_of_birth = models.DateField(
        verbose_name=_("date of birth"), blank=True, null=True
    )
    ahv_number = models.CharField(
        max_length=20, blank=True, verbose_name=_("ahv number")
    )
    notes = models.TextField(blank=True, verbose_name=_("notes"))

    insurance_documents = models.FileField(blank=True, upload_to="documents-jury/")
    photo = models.ImageField(blank=True, upload_to="photos-jury/")

    payee = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("payee"),
        help_text=_("name of the person receiving the payment"),
    )
    iban = models.CharField(max_length=35, blank=True, verbose_name=_("IBAN"))
    bic = models.CharField(max_length=20, blank=True, verbose_name=_("BIC"))
    bank_info = models.CharField(
        max_length=280, blank=True, verbose_name=_("bank info")
    )

    means_of_travel = models.CharField(
        max_length=120, blank=True, verbose_name=_("means of travel")
    )

    date_of_arrival = models.DateTimeField(
        blank=True, null=True, verbose_name=_("date of arrival")
    )
    transport_arrival = models.BooleanField(
        default=False,
        verbose_name=_("need transport on arrival"),
        help_text=_("do you need transport on arrival?"),
    )
    location_of_arrival = models.CharField(
        max_length=130, blank=True, verbose_name=_("location of arrival")
    )
    terminal_of_arrival = models.CharField(
        max_length=130, blank=True, verbose_name=_("terminal of arrival")
    )

    date_of_departure = models.DateTimeField(
        blank=True, null=True, verbose_name=_("date of departure")
    )
    transport_departure = models.BooleanField(
        default=False, verbose_name=_("need transport on departure")
    )
    location_of_departure = models.CharField(
        max_length=130, blank=True, verbose_name=_("location of departure")
    )
    terminal_of_departure = models.CharField(
        max_length=130, blank=True, verbose_name=_("terminal of departuree")
    )

    notes_tranpsort = models.TextField(blank=True, verbose_name=_("notes on transport"))


class Correpetitor(PersonBase):
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
    return f"{uploader.uid}/recordings/{filename}"


class Recording(models.Model):
    requirement = models.ForeignKey(RequiredRecording, models.CASCADE)
    recording = models.FileField(
        upload_to=recording_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "mp4",
                    "avi",
                    "mov",
                    "mkv",
                    "m4v",
                ]
            )
        ],
    )
    uploader = models.ForeignKey("Inscription", models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.recording.name.rsplit("/")[-1]


def generate_secret_id():
    return secrets.token_hex(4)


class Inscription(PersonBase):
    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    is_qualified = models.BooleanField(default=False, verbose_name=_("qualified"))
    secret_id = models.CharField(max_length=8, default=generate_secret_id)
    instrument = models.ForeignKey(
        Instrument, models.CASCADE, verbose_name=_("instrument")
    )
    internal_note = models.CharField(max_length=120, blank=True)

    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, verbose_name=_("gender")
    )

    date_of_birth = models.DateField(verbose_name=_("date of birth"))

    nationality = CountryField(verbose_name=_("nationality"))

    mother_tongue = models.CharField(max_length=120, verbose_name=_("language"))
    language_of_correspondence = models.CharField(
        max_length=120,
        choices=LANGUAGE_OF_CORRESPONDENCES,
        verbose_name=_("language of correspondence"),
    )

    education = models.TextField(max_length=500, verbose_name=_("artistic CV"))
    occupation = models.CharField(max_length=60, verbose_name=_("occupation"))
    notes = models.TextField(
        blank=True,
        verbose_name=_("notes"),
        help_text=_(
            "any information that we should know beforehand, not mentioned otherwise in this form"
        ),
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
        help_text=_(
            "how are you related to your emergency contact, (family, friends, ...)"
        ),
    )

    accomodation_needed = models.BooleanField(
        verbose_name=_("accomodation needed"),
        help_text=_("do you need us to organise accomodation?"),
    )
    is_smoker = models.BooleanField(verbose_name=_("smoker"))
    vegetarian = models.BooleanField(verbose_name=_("vegetarian"))

    allergies = models.CharField(
        max_length=120, blank=True, verbose_name=_("allergies")
    )

    host_family = models.ForeignKey(
        "HostFamily",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    has_documents = models.BooleanField(default=False)
    has_recordings = models.BooleanField(default=False)

    passport = models.FileField(blank=True, upload_to="documents/")
    photo = models.ImageField(blank=True, upload_to="photos/")

    payment = models.FloatField(default=0)
    payment_date = models.DateTimeField(blank=True, null=True)

    date_of_arrival = models.DateField(blank=True, null=True)
    time_of_arrival = models.TimeField(blank=True, null=True)

    def uploaded_recordings(self):
        return Recording.objects.filter(uploader=self).exclude(recording="").count()

    def total_recordings(self):
        return RequiredRecording.objects.filter(instrument=self.instrument).count()

    def setlists_complete(self):
        return (
            Selection.objects.filter(inscription=self, is_valid=True).count()
            == SetList.objects.filter(round__instrument=self.instrument).count()
        )

    def todos(self):
        todos = []

        if self.uploaded_recordings() < self.total_recordings():
            todos.append(_("Upload required recordings"))
        print(self.passport)
        if not self.passport:
            todos.append(_("Upload scan of your passport"))
        if not self.photo:
            todos.append(_("Upload a photo of yourself"))
        if not self.setlists_complete():
            todos.append(_("Select your pieces"))

        return todos

    def get_absolute_url(self):
        return reverse("tmc:inscription_detail", kwargs={"pk": self.pk})


class HostFamily(PersonBase):
    single_rooms = models.PositiveSmallIntegerField(
        verbose_name=_("no of single rooms"),
        help_text=_("how many single rooms can you provide?"),
    )
    double_rooms = models.PositiveSmallIntegerField(
        verbose_name=_("no of double rooms"),
        help_text=_(
            "how many rooms for two people can you provide? Below you can attach notes if necessary."
        ),
    )

    provides_breakfast = models.BooleanField(
        verbose_name=_("breakfast provided"), help_text=_("can you provide breakfast?")
    )

    has_own_bathroom = models.BooleanField(
        verbose_name=_("own bathroom"),
        help_text=_("do guests have their own bathroom?"),
    )
    has_wifi = models.BooleanField(
        verbose_name=_("wifi"), help_text=_("can guests use your wifi?")
    )
    provides_transport = models.BooleanField(
        verbose_name=_("transport"),
        help_text=_("do you provide transport for the contestants?"),
    )

    preferred_gender = models.CharField(
        max_length=5,
        choices=GENDER_CHOICES[:-1],
        blank=True,
        verbose_name=_("preferred gender"),
    )

    languages = models.ManyToManyField(
        Language,
        verbose_name=_("languages"),
        help_text=_("what languages do you speak?"),
    )

    pets = models.CharField(
        blank=True,
        max_length=180,
        verbose_name=_("pets"),
        help_text=_("do you have pets and if yes what kind?"),
    )
    practice_allowed = models.BooleanField(
        verbose_name=_("practice_allowed"),
        help_text=_("are contestants allowed to practice?"),
    )
    practice_notes = models.CharField(
        blank=True,
        max_length=180,
        verbose_name=_("practice notes"),
        help_text=_("are there any restrictions for practicing? Time, duration, ..."),
    )

    smoking_allowed = models.BooleanField(verbose_name=_("smokers allowed"))
    notes = models.TextField(blank=True, verbose_name=_("notes"))

    def __str__(self):
        return f"{self.given_name} {self.surname}"

    def get_absolute_url(self):
        return reverse("tmc:host_detail", kwargs={"pk": self.pk})

    def number_of_rooms(self):
        return self.single_rooms * 1 + self.double_rooms * 2


class Ressort(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class DateSlot(models.Model):
    date = models.DateField()
    note = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.date} ({self.note})"


class TimeSlot(models.Model):
    helper = models.ForeignKey("Helper", models.CASCADE)
    date = models.ForeignKey(DateSlot, models.CASCADE, verbose_name=_("datum"))

    SLOTS = (
        ("morning", _("Morning")),
        ("afternoon", _("Afternoon")),
        ("evening", _("Evening")),
        ("whole_day", _("Whole Day")),
    )
    slot = models.CharField(max_length=60, choices=SLOTS, verbose_name=_("slot"))

    def __str__(self):
        return str(self.helper)


class Helper(PersonBase):
    slots = models.ManyToManyField(DateSlot, through=TimeSlot, verbose_name=_("slots"))
    languages = models.ManyToManyField(Language, verbose_name=_("languages"))
    other_languages = models.CharField(
        max_length=120, blank=True, verbose_name=_("other languages")
    )

    ressorts = models.ManyToManyField(Ressort, verbose_name=_("ressorts"))
    other_ressorts = models.CharField(
        max_length=200, blank=True, verbose_name=_("other ressorts")
    )

    is_spontaneous = models.BooleanField(
        verbose_name=_("spontaneous?"), help_text=_("are you available spontaneously")
    )
    notes = models.TextField(blank=True, verbose_name=_("notes"))


class Round(models.Model):
    name = models.CharField(max_length=120)
    instrument = models.ForeignKey(Instrument, models.CASCADE)

    def __str__(self) -> str:
        return self.name


class SetList(models.Model):
    name = models.CharField(max_length=120)
    round = models.ForeignKey(Round, models.CASCADE)
    required = models.FloatField(default=1)

    def is_valid_selection(self, pieces):
        if sum([piece.value for piece in pieces]) != self.required:
            raise ValidationError("The selected amount of pieces is wrong.")
        piece_set = set(pieces)

        for piece in pieces:
            excludes = set(piece.excludes.all())
            overlapp = piece_set.intersection(excludes)
            if len(overlapp) > 0:
                raise ValidationError(
                    f"The selection of {piece} prevents the selection of {','.join({piece.name for piece in overlapp})}"
                )
        return True

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["round__name", "name"]


class Piece(models.Model):
    name = models.CharField(max_length=300)
    set_list = models.ForeignKey(SetList, models.CASCADE)
    excludes = models.ManyToManyField("self", blank=True)
    value = models.FloatField(default=1)

    def __str__(self) -> str:
        return self.name


class Selection(models.Model):
    set_list = models.ForeignKey(SetList, models.CASCADE)
    pieces = models.ManyToManyField(Piece)
    inscription = models.ForeignKey[Inscription](Inscription, models.CASCADE)

    is_valid = models.BooleanField(default=False)

    class Meta:
        ordering = ["set_list"]

    def round(self):
        return self.set_list.round

    def list_pieces(self):
        return ",".join([piece.name for piece in self.pieces.all()])

    def instrument(self):
        return self.set_list.round.instrument
