from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={"class": "form-control mb-2", 'placeholder': 'Логин'}))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(
                                   attrs={"class": "form-control mb-2", 'placeholder': 'Пароль'}))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control mb-2", 'placeholder': 'Логин'}))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control mb-2", 'placeholder': 'E-Mail'}))
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control mb-2", 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control mb-2", 'placeholder': 'Введите пароль еще раз'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
