import csv
import io

import pandas as pd
from django.contrib import admin
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import (
    ExportActionMixin,
    HttpResponse,
    ImportExportMixin,
)

from tmc.forms import HostAdminForm
from tmc.models import (
    DateSlot,
    Helper,
    HostFamily,
    Inscription,
    Instrument,
    JuryMember,
    Language,
    Piece,
    Recording,
    RequiredRecording,
    Ressort,
    Round,
    Selection,
    SetList,
    TimeSlot,
)

# Register your models here.


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name",)


class InscriptionResource(resources.ModelResource):
    class Meta:
        model = Inscription


@admin.register(RequiredRecording)
class RequiredRecordingAdmin(admin.ModelAdmin):
    list_display = ("name", "nr", "instrument", "slug")
    list_filter = ("instrument",)


class RecordingInline(admin.TabularInline):
    model = Recording
    extra = 0


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("requirement", "__str__", "uploader", "created", "updated")
    list_filter = ("requirement", "uploader", "requirement__instrument")


@admin.action(description=_("Check for recordings and documents"))
def check_recordings(modeladmin, request, queryset):
    queryset.filter(Q(photo="") | Q(passport="")).update(has_documents=False)
    queryset.exclude(Q(photo="") | Q(passport="")).update(has_documents=True)

    queryset.filter(recording__isnull=False).update(has_recordings=True)
    queryset.filter(recording__isnull=True).update(has_recordings=False)


@admin.action(description="Download recording playlist")
def download_playlist(modeladmin, request, queryset):
    recordings = Recording.objects.filter(uploader__in=queryset).order_by(
        "uploader__secret_id", "requirement__nr"
    )

    results = []
    for recording in recordings:
        results.append(
            {
                "id": recording.uploader.secret_id,
                "url": recording.recording.url,
                "name": recording.requirement.name,
            }
        )

    response = HttpResponse(
        content_type="text/m3u",
        headers={"Content-Disposition": 'attachment; filename="recordings.m3u"'},
    )

    response.write("#EXTM3U\n\n")
    for i, result in enumerate(results):
        line = f'#EXTINF:{i:03}, {result["id"]} - {result["name"]}\n{result["url"]}\n'
        response.write(line)

    return response


def read_repertoire_df(queryset: QuerySet[Selection]):
    results = []

    for row in queryset:
        results.append(
            {
                "id": row.inscription.pk,
                "secret_id": row.inscription.secret_id,
                "first name": row.inscription.given_name,
                "last name": row.inscription.surname,
                "round": str(row.round()) + " - " + str(row.set_list.name),
                "pieces": ",".join(
                    row.pieces.values_list("name", flat=True),
                ),
            }
        )

    df = pd.DataFrame.from_records(results)

    names = df.drop_duplicates("id").set_index("id")[
        ["first name", "last name", "secret_id"]
    ]
    pieces = df.pivot(index="id", columns="round", values=["pieces"])
    pieces.columns = pieces.columns.droplevel(0)

    output = io.BytesIO()

    names.join(pieces).to_excel(output)
    output.seek(0)

    return output.read()


@admin.action(description="Download repertoire")
def download_repertoire(modeladmin, request, queryset):
    return HttpResponse(
        read_repertoire_df(queryset),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="repertoire.xlsx"'},
    )


@admin.action(description="Download recording url list")
def download_info(modeladmin, request, queryset):
    recordings = Recording.objects.filter(uploader__in=queryset).order_by(
        "uploader__secret_id", "requirement__nr"
    )

    results = []
    for recording in recordings:
        id = recording.uploader.secret_id
        nr = recording.requirement.nr
        slug = recording.requirement.slug
        extension = recording.recording.name.split(".")[-1]
        results.append(
            {
                "id": id,
                "url": recording.recording.url,
                "name": recording.requirement.name,
                "slug": slug,
                "target": f"{id}/{nr:02}_{slug}.{extension}",
            }
        )

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="recordings.csv"'},
    )

    writer = csv.DictWriter(response, ["id", "url", "name", "slug", "target"])
    writer.writeheader()
    writer.writerows(results)
    return response


@admin.action(description="Enumerate inscriptions (random)")
def enumerate_inscriptions(modeladmin, request, queryset):
    with transaction.atomic():
        queryset = queryset.order_by("?")

        for i, q in enumerate(queryset):
            q.secret_id = f"{i+1:04}"
            q.save()


@admin.register(Inscription)
class InscriptionAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    resource_class = InscriptionResource

    list_filter = (
        "instrument",
        "is_qualified",
        "gender",
        "accomodation_needed",
        "is_smoker",
        "food_needed",
        "vegetarian",
        "has_recordings",
        "has_documents",
    )
    list_display = (
        "given_name",
        "surname",
        "is_qualified",
        "internal_note",
        "instrument",
        "nationality",
        "language_of_correspondence",
        "email",
        "phone",
        "secret_id",
        "uploaded_recordings",
    )
    date_hierarchy = "submitted_at"
    search_fields = (
        "given_name",
        "surname",
        "email",
    )

    list_editable = ["is_qualified"]

    readonly_fields = ["submitted_at"]

    inlines = [RecordingInline]
    actions = [
        check_recordings,
        download_playlist,
        download_info,
        enumerate_inscriptions,
    ]


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0

    fields = (
        "given_name",
        "surname",
        "gender",
        "date_of_birth",
        "is_smoker",
        "vegetarian",
        "accomodation_needed",
    )
    readonly_fields = fields


@admin.register(HostFamily)
class HostFamilyAdmin(admin.ModelAdmin):
    form = HostAdminForm
    list_display = ("given_name", "surname", "email", "single_rooms", "double_rooms")
    list_filter = (
        "provides_breakfast",
        "has_wifi",
        "provides_breakfast",
        "practice_allowed",
        "smoking_allowed",
    )

    def save_model(self, request, obj: HostFamily, form, change):
        super().save_model(request, obj, form, change)
        print(type(form.cleaned_data["guests"]))
        obj.inscription_set.set(form.cleaned_data["guests"])


class SlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 0


@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    list_display = ("given_name", "surname", "email")
    inlines = [SlotInline]


@admin.register(DateSlot)
class DateSlotAdmin(admin.ModelAdmin):
    list_display = ("date", "note")


@admin.register(Ressort)
class RessortAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(JuryMember)
class JuryMemberAdmin(admin.ModelAdmin):
    list_display = ("given_name", "surname", "email")
    list_editable = ("email",)
    list_filter = ("transport_arrival", "transport_departure", "means_of_travel")


class SetListInline(admin.TabularInline):
    model = SetList


class PieceInline(admin.TabularInline):
    model = Piece


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ["name", "instrument"]
    inlines = [SetListInline]


@admin.register(SetList)
class SetlistAdmin(admin.ModelAdmin):
    list_display = ["name", "round"]
    inlines = [PieceInline]


@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ["name", "set_list"]


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = [
        "inscription",
        "round",
        "instrument",
        "set_list",
        "list_pieces",
        "is_valid",
    ]
    list_filter = ["is_valid", "set_list__round__instrument"]
    readonly_fields = ["pieces"]

    actions = [download_repertoire]
