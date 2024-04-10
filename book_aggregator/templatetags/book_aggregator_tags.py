from django import template
from book_aggregator.models import Book, Category, Comment
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('book_aggregator/categories.html')
def show_categories():
    categories = Category.objects.all()
    return {'categories': categories}


@register.inclusion_tag('book_aggregator/latest_books.html')
def show_latest_books():
    latest_books = Book.objects.all().order_by('-added_at')[:9]
    return {'latest_books': latest_books}


@register.inclusion_tag('book_aggregator/highest_rating_books.html')
def show_highest_rating_books():
    highest_rating_books = Book.objects.all().order_by('-avg_rating')[:9]
    return {'highest_rating_books': highest_rating_books}


@register.inclusion_tag('book_aggregator/most_commented_books.html')
def show_most_commented_books():
    comments = Comment.objects.annotate(
        comments_count=Count('book')).order_by('-comments_count')[:9]

    most_commented_books = set([comment.book for comment in comments])
    if len(most_commented_books) < 9:
        books = list(Book.objects.all()[:9 - len(most_commented_books)])
        most_commented_books = list(most_commented_books) + books
    return {'most_commented_books': most_commented_books}
