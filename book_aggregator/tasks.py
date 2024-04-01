from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from BookAggregator.celery import app
from book_aggregator.models import Book
from get_new_books import get_books
from book_aggregator.views import add_books


@app.task
def get_new_books():
    get_books()
    add_books()
