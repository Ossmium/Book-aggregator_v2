from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse


class Category(models.Model):
    name = models.CharField()
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book_aggregator:category', args=[self.slug])


class SubCategory(models.Model):
    name = models.CharField()
    slug = models.SlugField(max_length=1000)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book_aggregator:category', args=[self.slug])


class Book(models.Model):
    name = models.CharField()
    author = models.CharField(null=True)
    categories = ArrayField(models.CharField(), default=list)
    image_url = models.CharField(null=True)
    genres = ArrayField(models.CharField(), default=list)
    description = models.TextField()
    avg_rating = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    have_electronic_version = models.BooleanField()
    have_physical_version = models.BooleanField()
    sources = models.JSONField()
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    url = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=1000)
    price_stats = models.JSONField(default=dict())
    users = models.ManyToManyField(User, related_name='favourite_books')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book_aggregator:detail', args=[self.url])


class Comment(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="books")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.book}'


class RatingStar(models.Model):
    value = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Звезда рейтинга'
        verbose_name_plural = 'Звезды рейтинга'
        ordering = ['-value']

    def __str__(self):
        return f'{self.value}'


class Rating(models.Model):
    star = models.ForeignKey(
        RatingStar, on_delete=models.CASCADE, verbose_name='Оценка')
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    # def __str__(self):
    #     return f'{self.post}: {self.star}'
