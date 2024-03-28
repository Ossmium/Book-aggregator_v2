from django.contrib import admin
from book_aggregator.models import Book, Category, SubCategory, RatingStar

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(RatingStar)
