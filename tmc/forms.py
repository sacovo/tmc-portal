from crispy_forms.layout import Submit
from django import forms
from django.urls.base import reverse
from django.utils.translation import gettext as _
from crispy_forms.helper import FormHelper
from django.forms.widgets import DateInput

from tmc.models import Inscription, Recording


class SignupForm(forms.ModelForm):

    class Meta:
        model = Inscription
        fields = [
            'given_name',
            'surname',
            'instrument',
            'gender',
            'date_of_birth',
            'nationality',
            'address',
            'mother_tongue',
            'language_of_correspondence',
            'phone',
            'email',
            'education',
            'occupation',
            'notes',
            'emergency_contact',
            'emergency_phone',
            'emergency_relation',
            'accomodation_needed',
            'is_smoker',
            'food_needed',
            'vegetarian',
            'allergies',
        ]
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_signup"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Submit")))


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Inscription
        fields = ['photo', 'passport']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_documents"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Submit")))


class LoginForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        inscription = Inscription.objects.filter(email=email).first()

        if inscription is None:
            raise forms.ValidationError(_("This e-mail is not registered."))
        return inscription

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_login"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Login")))
