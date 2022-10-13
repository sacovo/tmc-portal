from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from crispy_forms.helper import FormHelper
from django.forms.widgets import DateInput

from tmc.models import Helper, HostFamily, Inscription, JuryMember


class UserSignupMixin:

    def clean_email(self):
        email = self.cleaned_data['email']

        if self.instance is not None:
            return email

        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This e-mail is already registered")

        return email


class SignupForm(forms.ModelForm, UserSignupMixin):

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
        user = get_user_model().objects.filter(email=email).first()

        if user is None:
            raise forms.ValidationError(_("This e-mail is not registered."))

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_login"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Login")))


class HostForm(forms.ModelForm, UserSignupMixin):

    class Meta:
        model = HostFamily
        fields = [
            'given_name',
            'surname',
            'address',
            'phone',
            'email',
            'single_rooms',
            'double_rooms',
            'provides_breakfast',
            'has_own_bathroom',
            'has_wifi',
            'provides_transport',
            'preferred_gender',
            'pets',
            'practice_allowed',
            'practice_notes',
            'smoking_allowed',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_host"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Submit")))


class HelperForm(forms.ModelForm, UserSignupMixin):

    class Meta:
        model = Helper
        fields = [
            'given_name',
            'surname',
            'address',
            'phone',
            'email',
            'notes',
            'languages',
            'other_languages',
            'ressorts',
            'other_ressorts',
            'is_spontaneous',
        ]

        widgets = {
            'ressorts': forms.CheckboxSelectMultiple(),
            'languages': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = "id_helper"


class SlotFormsetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_method = 'post'
        self.form_id = 'id_formset'
        self.form_class = 'horizontal'
        self.template = 'bootstrap/table_inline_formset.html'
        self.add_input(Submit("submit", _("Submit")))


class JuryForm(forms.ModelForm, UserSignupMixin):

    class Meta:
        model = JuryMember
        fields = [
            'given_name',
            'surname',
            'address',
            'phone',
            'email',
            'notes',
            'instrument',
            'kind',
            'date_of_birth',
            'ahv_number',
            'payee',
            'iban',
            'bic',
            'means_of_travel',
            'date_of_arrival',
            'transport_arrival',
            'location_of_arrival',
            'terminal_of_arrival',
            'date_of_departure',
            'transport_departure',
            'location_of_departure',
            'terminal_of_departure',
            'notes_tranpsort',
        ]

        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'date_of_arrival': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'date_of_departure': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_jury"
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", _("Submit")))
        self.helper.layout = Layout(
            Fieldset(
                _("This is a legend"),
                'given_name',
                'surname',
                'address',
                'phone',
                'email',
                'notes',
                'instrument',
                'date_of_birth',
                'ahv_number',
            ),
            HTML('<hr/>'),
            Fieldset(
                _("Bank information"),
                'payee',
                'iban',
                'bic',
            ),
            HTML('<hr/>'),
            Fieldset(
                _("Travel information"),
                'means_of_travel',
                'date_of_arrival',
                'transport_arrival',
                'location_of_arrival',
                'terminal_of_arrival',
                'date_of_departure',
                'transport_departure',
                'location_of_departure',
                'terminal_of_departure',
                'notes_tranpsort',
            ),
        )
