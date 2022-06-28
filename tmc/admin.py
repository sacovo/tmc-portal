from django.contrib import admin

from import_export.admin import ExportActionMixin, ImportExportMixin

from tmc.models import HostFamily, Inscription, Instrument, Language, Recording, RequiredRecording
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


@admin.register(Inscription)
class InscriptionAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    resource_class = InscriptionResource

    list_filter = (
        'instrument',
        'gender',
        'nationality',
        'accomodation_needed',
        'is_smoker',
        'food_needed',
        'vegetarian',
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
