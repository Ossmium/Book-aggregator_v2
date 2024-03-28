from django import template
from book_aggregator.models import Book, Category

register = template.Library()


@register.inclusion_tag('book_aggregator/categories.html')
def show_categories():
    categories = Category.objects.all()
    return {'categories': categories}


@register.inclusion_tag('book_aggregator/latest_books.html')
def show_latest_books():
    latest_books = Book.objects.all().order_by('-added_at')[:9]
    return {'latest_books': latest_books}
