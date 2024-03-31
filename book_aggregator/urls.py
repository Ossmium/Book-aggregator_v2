from django.urls import path
from book_aggregator import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.book_search, name='book_search'),
    path('genre/<slug:category_slug>/', views.category, name='category'),

    path('books/<slug:book_slug>/comment/',
         views.book_comment, name='comment'),
    path('books/<slug:book_slug>/', views.book_detail, name='detail'),

    path('profile/favourite/', views.user_favourite_books, name='favourite_books'),
]
