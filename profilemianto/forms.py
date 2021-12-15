from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django import forms
from .models import ProfileMianto


class LoginProfileForm(forms.Form):
    """
    Класс форм для входа в профиль
    """
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('email', css_class='form-group col-md-4 md-0'), css_class='form-row'),
            Row(Column('password', css_class='form-group col-md-4 mb-0'), css_class='form-row'),
            Submit('submit', "Войти"),
            HTML("<a class='btn btn-primary' href='{% url \"profileregister\" %}'>Регистрация")
        )


class RegisterProfileForm(forms.ModelForm):
    """
    Класс форм для регистрации в системе
    """

    class Meta:
        model = ProfileMianto
        fields = ['login', 'password', 'email', 'dob', 'gender', 'avatar']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dob'].required = True
        self.fields['gender'].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('login', css_class='form-group col-md-2 mb-0'),
                Column('email', css_class='form-group col-md-2 mb-0'),
                Column('password', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
                ),
            Row(Column('avatar', css_class='form-group col-md-6 md-0'), css_class='form-row'),
            Row(Column('gender', css_class='form-group col-md-3 mb-0'),
                Column('dob', css_class='form-group col-md-3 mb-0'), css_class='form-row'),
            Submit('submit', 'Зарегистрироваться')
        )


class UpdateProfileForm(forms.ModelForm):
    """
    Класс форм для регистрации в системе
    """

    class Meta:
        model = ProfileMianto
        fields = ['login', 'email', 'gender', 'avatar']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('login', css_class='form-group col-md-3 mb-0'),
                Column('email', css_class='form-group col-md-3 mb-0'),
                Column('gender', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
                ),
            Row(Column('avatar', css_class='form-group col-md-9 md-0'), css_class='form-row'),
            Submit('submit', 'Сохранить')
        )
