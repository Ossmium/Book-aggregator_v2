from .models import Profile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={
                                   "class": "form-control",
                                   'id': 'floatingUsername',
                               }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(
                                   attrs={
                                       "class": "form-control mb-2",
                                       'id': 'floatingPassword'
                                   }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            "class": "form-control mb-2",
            'id': 'floatingUsername',
            'placeholder': 'Логин',
        }))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            "class": "form-control mb-2",
            'id': 'floatingEmail',
            'placeholder': 'E-mail',
        }))
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={
            "class": "form-control mb-2",
            'id': 'floatingPassword1',
            'placeholder': 'Пароль',
        }))
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={
            "class": "form-control mb-2",
            'id': 'floatingPassword2',
            'placeholder': 'Подтвердите пароль',
        }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(
                                   attrs={'id': 'floatingUsername',
                                          'class': 'form-control mt-3 mb-3',
                                          'placeholder': 'Логин',
                                          }
                               ))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(
                                 attrs={'id': 'floatingEmail',
                                        'class': 'form-control',
                                        'placeholder': 'E-mail',
                                        }
                             ))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'id': 'formAvatar',
            }))
    about = forms.CharField(widget=forms.Textarea(
        attrs={'id': 'floatingAbout',
               'class': 'form-control',
               'placeholder': 'О себе',
               'style': 'min-height: 200px;'}),
        required=False)

    class Meta:
        model = Profile
        fields = ['avatar', 'about']
