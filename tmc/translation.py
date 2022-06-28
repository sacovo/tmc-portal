from modeltranslation.translator import translator, TranslationOptions
from .models import Instrument


class InstrumentTranslationOptions(TranslationOptions):
    fields = ('name', )


translator.register(Instrument, InstrumentTranslationOptions)
