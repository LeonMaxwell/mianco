from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.urls import reverse_lazy
from bootstrap_datepicker_plus import DatePickerInput
from area.models import City
from dal import autocomplete
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Announcement


class ContactForm(forms.Form):
    """ Класс форм выводящий каптчу """
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label="")


class SettingsForm(forms.ModelForm):
    """
    Класс форм который предоставляет пользователю отфильтровать объявления по своему вкусу.
    """

    from_age = forms.ChoiceField(label="Возраст от", choices=((x, x) for x in range(18, 81)))
    to_age = forms.ChoiceField(label="до", choices=((x, x) for x in range(18, 81)))

    class Meta:
        model = Announcement
        fields = ['gender', 'interlocutor', 'purpose_of_acquaintance', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('gender', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(Column('interlocutor', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(Column('purpose_of_acquaintance', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(
                Column('from_age', css_class='form-group col-md-4 mb-0'),
                Column('to_age', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'),
            Row(Column('city', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Submit('submit', 'Применить настройки')
        )


class CreateAdForm(forms.ModelForm):
    """
    Класс форм при котором создаются объявления.
    """

    class Meta:
        model = Announcement
        fields = ['email', 'dob', 'text', 'gender', 'interlocutor', 'purpose_of_acquaintance',
                  'city']
        widgets = {
            'dob': DatePickerInput(format="YYYY-MM-DD"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('email', css_class='form-group col-md-4 mb-0'),
                Column('dob', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
                ),
            Row(Column('text', css_class='form-group col-md-8 md-0'), css_class='form-row'),
            Row(Column('gender', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(Column('interlocutor', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(Column('purpose_of_acquaintance', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Row(Column('city', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Submit('submit', 'Создать объявление')
        )


class AnswerForm(forms.Form):
    """ Класс формы ответа на объявление. """
    email = forms.EmailField(label="Введите вашу почту", max_length=255)
    answer = forms.CharField(widget=forms.Textarea, label="Напишите ответ", max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('email', css_class='form-group col-md-8 md-0'), css_class='form-row'),
            Row(Column('answer', css_class='form-group col-md-8 mb-0'), css_class='form-row'),
            Submit('submit', 'Ответить на объявление')
        )