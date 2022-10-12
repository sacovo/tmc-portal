from django.contrib import admin
from django.db.models import Q

from import_export.admin import ExportActionMixin, ImportExportMixin
from django.utils.translation import gettext as _

from tmc.models import DateSlot, Helper, HostFamily, Inscription, Instrument, JuryMember, Language, Recording, RequiredRecording, Ressort, TimeSlot
from import_export import resources

# Register your models here.


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', )


class InscriptionResource(resources.ModelResource):

    class Meta:
        model = Inscription


@admin.register(RequiredRecording)
class RequiredRecordingAdmin(admin.ModelAdmin):
    list_display = ('name', 'nr', 'instrument', 'slug')
    list_filter = ('instrument', )


class RecordingInline(admin.TabularInline):
    model = Recording
    extra = 0


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ('requirement', '__str__', 'uploader', 'created', 'updated')
    list_filter = ('requirement', 'uploader', 'requirement__instrument')


@admin.action(description=_("Check for recordings and documents"))
def check_recordings(modeladmin, request, queryset):
    has_passport = Q(passport__isnull=False)
    has_photo = Q(photo__isnull=False)

    queryset.filter(has_photo & has_passport).update(has_documents=True)
    queryset.exclude(has_photo & has_passport).update(has_documents=False)

    queryset.filter(recording__isnull=False).update(has_recordings=True)
    queryset.filter(recording__isnull=True).update(has_recordings=False)


@admin.register(Inscription)
class InscriptionAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    resource_class = InscriptionResource

    list_filter = (
        'instrument',
        'gender',
        'accomodation_needed',
        'is_smoker',
        'food_needed',
        'vegetarian',
        'has_recordings',
        'has_documents',
    )
    list_display = (
        'given_name',
        'surname',
        'instrument',
        'nationality',
        'language_of_correspondence',
        'email',
        'phone',
        'secret_id',
        'uploaded_recordings',
    )
    date_hierarchy = 'submitted_at'
    search_fields = (
        'name',
        'email',
    )

    readonly_fields = ['submitted_at']

    inlines = [RecordingInline]
    actions = [check_recordings]


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0

    fields = ('given_name', 'surname', 'gender', 'date_of_birth', 'is_smoker', 'vegetarian',
              'accomodation_needed')
    readonly_fields = fields


@admin.register(HostFamily)
class HostFamilyAdmin(admin.ModelAdmin):
    list_display = ('given_name', 'surname', 'email', 'single_rooms', 'double_rooms')
    list_filter = ('provides_breakfast', 'has_wifi', 'provides_breakfast', 'practice_allowed',
                   'smoking_allowed')
    inlines = [InscriptionInline]


class SlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 0


@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    list_display = ('given_name', 'surname', 'email')
    inlines = [SlotInline]


@admin.register(DateSlot)
class DateSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'note')


@admin.register(Ressort)
class RessortAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(JuryMember)
class JuryMemberAdmin(admin.ModelAdmin):
    list_display = ('given_name', 'surname', 'email')
    list_editable = ('email', )
    list_filter = ('transport_arrival', 'transport_departure', 'means_of_travel')
