from django.urls import reverse_lazy, reverse
from django.views import generic
from accounts.forms import SignUpForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from book_aggregator.models import Comment
from django.http import HttpResponseRedirect


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(CustomLoginView, self).form_valid(form)


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("accounts/login")
    initial = None
    template_name = "accounts/signup.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect(to='accounts/login')
        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')
        return super(SignUpView, self).dispatch(request, *args, **kwargs)


class ChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('accounts/profile')


def user_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    favourite_books = request.user.favourite_books.filter()
    commented_books = [comment.book for comment in Comment.objects.filter(
        name=request.user.username)]

    return render(request, 'accounts/user_books.html', context={
        'favourite_books': favourite_books[:9],
        'commented_books': commented_books[:9],
    })


def user_favourite_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    favourite_books = request.user.favourite_books.filter()

    return render(request, 'accounts/favourite_books.html', context={
        'favourite_books': favourite_books,
    })


def user_commented_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    commented_books = [comment.book for comment in Comment.objects.filter(
        name=request.user.username)]

    return render(request, 'accounts/commented_books.html', context={
        'commented_books': commented_books,
    })


def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {'user_form': user_form, 'profile_form': profile_form})
