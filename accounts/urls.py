from django.urls import path
from .views import SignUpView, CustomLoginView, user_books, user_favourite_books, user_commented_books
from django.contrib.auth import views as auth_views
from accounts.views import SignUpView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True,
         template_name='accounts/login.html'), name='login'),

    path('profile/books/', user_books, name='books'),
    path('profile/favourite/', user_favourite_books, name='favourite_books'),
    path('profile/comments/', user_commented_books, name='commented_books'),
]
