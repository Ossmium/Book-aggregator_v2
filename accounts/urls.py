from django.urls import path
from .views import SignUpView, CustomLoginView
from django.contrib.auth import views as auth_views
from accounts.views import SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True,
         template_name='accounts/login.html'), name='login'),
]
