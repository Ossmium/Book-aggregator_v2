from django.shortcuts import render, get_object_or_404
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist

from utils import add_book, add_subcategories
import json
from book_aggregator.models import Book, SubCategory, Category, Comment, Rating, RatingStar
from book_aggregator.forms import SearchForm, FilterForm, SortForm, CommentForm, RatingForm


def index(request):
    params = []
    books_list = Book.objects.all()
    books_subcategories = SubCategory.objects.all()

    if request.user.is_authenticated:
        print(request.user.favourite_books.filter())

    return render(request, "book_aggregator/index.html", context={
        # 'form': form,
        # 'filter_form': filter_form,
        # 'query': query,
        'books': books_list,
        'subcategories': books_subcategories,
    })


def category(request, category_slug):
    filter_form = FilterForm()
    sort_form = SortForm()
    query = None
    sort = None
    results = []
    params = []

    if category_slug:
        filter_form = FilterForm(request.GET)
        sort_form = SortForm(request.GET)

        if filter_form.is_valid() and sort_form.is_valid():
            if len(Category.objects.filter(slug=category_slug)):
                category = Category.objects.get(slug=category_slug)
                results = Book.objects.filter(categories__contains=[category])
            else:
                category = SubCategory.objects.get(slug=category_slug)
                results = Book.objects.filter(genres__contains=[category])
            # print(results)
            authors_set = set([book.author for book in results])
            genre_set = set(
                [genre for book in results for genre in book.genres])
            genre_set = [genre for genre in genre_set]
            for genre in genre_set:
                if category.name == genre:
                    genre_set.remove(genre)
                    print(genre)
                    break
            genre_choices_list = [(genre, genre)for genre in genre_set]
            # authors_arr = [(1, 1) for a]
            authors_choices_list = [[author, author]
                                    for author in authors_set]
            for author in authors_choices_list:
                if author[0] is None:
                    author[0], author[1] = 'Нет автора', 'Нет автора'
            # filter_form = FilterForm(
            #     request.GET, authors_choices=authors_choices_set)
            authors_choices_list = sorted(
                authors_choices_list, key=lambda x: x[1])
            genre_choices_list = sorted(
                genre_choices_list, key=lambda x: x[1])
            filter_form.fields['authors'].choices = authors_choices_list
            filter_form.fields['genre'].choices = genre_choices_list

            # print(len(authors_choices_set), authors_choices_set)
            # print(results)

    if 'authors' in request.GET:
        if len(Category.objects.filter(slug=category_slug)):
            category = Category.objects.get(slug=category_slug)
            results = Book.objects.filter(categories__contains=[category])
        else:
            category = SubCategory.objects.get(slug=category_slug)
            results = Book.objects.filter(genres__contains=[category])

        # form = SearchForm(request.GET)
        filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        authors_set = set(
            [book.author for book in results])
        genre_set = set(
            [genre for book in results for genre in book.genres])
        genre_set = [genre for genre in genre_set]
        for genre in genre_set:
            if category.name == genre:
                genre_set.remove(genre)
                print(genre)
                break
        # authors_arr = [(1, 1) for a]
        authors_choices_list = [[author, author]
                                for author in authors_set]
        genre_choices_list = [(genre, genre)for genre in genre_set]

        for author in authors_choices_list:
            if author[0] is None:
                author[0], author[1] = 'Нет автора', 'Нет автора'

        authors_choices_list = sorted(authors_choices_list, key=lambda x: x[1])
        genre_choices_list = sorted(genre_choices_list, key=lambda x: x[1])

        filter_form.fields['authors'].choices = authors_choices_list
        filter_form.fields['genre'].choices = genre_choices_list
        # filter_form = FilterForm(
        #     request.GET, authors_choices=authors_choices_set)
        # print(filter_form.fields['authors'].choices)
        if filter_form.is_valid() and sort_form.is_valid():
            authors = filter_form.cleaned_data['authors']
            # print(authors)
            if results != []:
                results = results.filter(author__in=authors)
            else:
                results = Book.objects.filter(author__in=authors)
            for author in authors:
                params.append(('authors', author))
            # results = Book.objects.annotate(
            #     similarity=TrigramSimilarity('name', query),
            # ).filter(similarity__gt=0.1).order_by('-similarity')

    if 'genre' in request.GET:
        if len(Category.objects.filter(slug=category_slug)):
            category = Category.objects.get(slug=category_slug)
            results = Book.objects.filter(categories__contains=[category])
        else:
            category = SubCategory.objects.get(slug=category_slug)
            results = Book.objects.filter(genres__contains=[category])

        filter_form = FilterForm(request.GET)

        authors_set = set(
            [book.author for book in results])
        genre_set = set(
            [genre for book in results for genre in book.genres])
        genre_set = [genre for genre in genre_set]
        for genre in genre_set:
            if category.name == genre:
                genre_set.remove(genre)
                print(genre)
                break
        # authors_arr = [(1, 1) for a]
        authors_choices_list = [[author, author]
                                for author in authors_set]
        genre_choices_list = [(genre, genre)for genre in genre_set]

        for author in authors_choices_list:
            if author[0] is None:
                author[0], author[1] = 'Нет автора', 'Нет автора'

        authors_choices_list = sorted(authors_choices_list, key=lambda x: x[1])
        genre_choices_list = sorted(genre_choices_list, key=lambda x: x[1])

        filter_form.fields['authors'].choices = authors_choices_list
        filter_form.fields['genre'].choices = genre_choices_list

        if filter_form.is_valid() and sort_form.is_valid():
            genres = filter_form.cleaned_data['genre']
            if results != []:
                results = results.filter(genres__overlap=genres)
            else:
                results = Book.objects.filter(genres__overlap=genres)
            for genre in genres:
                params.append(('genre', genre))

    # if 'price_from' in request.GET:
    #     form = SearchForm(request.GET)
    #     filter_form = FilterForm(request.GET)
    #     sort_form = SortForm(request.GET)
    #     # search_form = SearchForm()
    #     if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
    #         query = form.cleaned_data['query']
    #         price_from = filter_form.cleaned_data['price_from']
    #         if results != []:
    #             results = results.filter(min_price__gt=price_from)
    #         else:
    #             results = Book.objects.filter(min_price__gt=price_from)

    # if 'price_to' in request.GET:
    #     form = SearchForm(request.GET)
    #     filter_form = FilterForm(request.GET)
    #     sort_form = SortForm(request.GET)
    #     # search_form = SearchForm()
    #     if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
    #         query = form.cleaned_data['query']
    #         price_to = filter_form.cleaned_data['price_to']
    #         if results != []:
    #             results = results.filter(min_price__lt=price_to)
    #         else:
    #             results = Book.objects.filter(min_price__lt=price_to)

    if 'more_than_four' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if filter_form.is_valid() and sort_form.is_valid():
            more_than_four = filter_form.cleaned_data['more_than_four']
            if results != []:
                if more_than_four:
                    results = results.filter(avg_rating__gt=4)
            else:
                if more_than_four:
                    results = Book.objects.filter(avg_rating__gt=4)
            params.append(('more_than_four', more_than_four))

    if 'have_electronic' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if filter_form.is_valid() and sort_form.is_valid():
            have_electronic = filter_form.cleaned_data['have_electronic']
            if results != []:
                if have_electronic:
                    results = results.filter(have_electronic_version=True)
            else:
                if have_electronic:
                    results = Book.objects.filter(have_electronic_version=True)
            params.append(('have_electronic', have_electronic))

    if 'have_physical' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if filter_form.is_valid() and sort_form.is_valid():
            have_physical = filter_form.cleaned_data['have_physical']
            if results != []:
                if have_physical:
                    results = results.filter(have_physical_version=True)
            else:
                if have_physical:
                    results = Book.objects.filter(have_physical_version=True)
            params.append(('have_physical', have_physical))

    if 'sort' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if filter_form.is_valid() and sort_form.is_valid():
            sort = sort_form.cleaned_data['sort']
            if results != []:
                if sort == 'default':
                    results = results
                elif sort == 'increase_price':
                    results = results.order_by('min_price')
                elif sort == 'decrease_price':
                    results = results.order_by('-min_price')
            else:
                if have_physical:
                    results = Book.objects.filter(have_physical_version=True)
            params.append(('sort', sort))
    # paginator = Paginator(results, 1)
    # page_number = request.GET.get('page', 1)
    # try:
    #     results = paginator.page(page_number)
    # except PageNotAnInteger:
    #     results = paginator.page(1)
    # except EmptyPage:
    #     results = paginator.page(paginator.num_pages)
    # print('Тут:', params)
    html = render(request, 'book_aggregator/categories_search.html', context={
        'params': params,
        'category': category,
        'filter_form': filter_form,
        'sort_form': sort_form,
        'books': results
    })
    if 'sort' in request.GET:
        html.set_cookie('sort', sort)
    return html


def book_search(request):
    form = SearchForm()
    filter_form = FilterForm()
    sort_form = SortForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        filter_form = FilterForm(request.GET)
        sort_form = SortForm(request.GET)

        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            results = Book.objects.annotate(
                similarity=TrigramSimilarity('name', query),
            ).filter(similarity__gt=0.2).order_by('-similarity')
            authors_set = set([book.author for book in results])
            genre_set = set(
                [genre for book in results for genre in book.genres])
            genre_choices_list = [(genre, genre)for genre in genre_set]
            # authors_arr = [(1, 1) for a]
            authors_choices_list = [(author, author)
                                    for author in authors_set]
            # filter_form = FilterForm(
            #     request.GET, authors_choices=authors_choices_set)
            authors_choices_list = sorted(
                authors_choices_list, key=lambda x: x[1])
            genre_choices_list = sorted(
                genre_choices_list, key=lambda x: x[1])
            filter_form.fields['authors'].choices = authors_choices_list
            filter_form.fields['genre'].choices = genre_choices_list
            # print(len(authors_choices_set), authors_choices_set)
            # print(results)

    if 'authors' in request.GET:
        query = form.cleaned_data['query']
        results = Book.objects.annotate(
            similarity=TrigramSimilarity('name', query),
        ).filter(similarity__gt=0.2).order_by('-similarity')
        print(results)
        # form = SearchForm(request.GET)
        filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        authors_set = set(
            [book.author for book in results])
        genre_set = set(
            [genre for book in results for genre in book.genres])
        # authors_arr = [(1, 1) for a]
        authors_choices_list = [(author, author)
                                for author in authors_set]
        genre_choices_list = [(genre, genre)for genre in genre_set]

        authors_choices_list = sorted(authors_choices_list, key=lambda x: x[1])
        genre_choices_list = sorted(genre_choices_list, key=lambda x: x[1])

        filter_form.fields['authors'].choices = authors_choices_list
        filter_form.fields['genre'].choices = genre_choices_list
        # filter_form = FilterForm(
        #     request.GET, authors_choices=authors_choices_set)
        # print(filter_form.fields['authors'].choices)
        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            authors = filter_form.cleaned_data['authors']
            print(authors)
            if results != []:
                results = results.filter(author__in=authors)
            else:
                results = Book.objects.filter(author__in=authors)
            # results = Book.objects.annotate(
            #     similarity=TrigramSimilarity('name', query),
            # ).filter(similarity__gt=0.1).order_by('-similarity')

    if 'genre' in request.GET:
        query = form.cleaned_data['query']
        results = Book.objects.annotate(
            similarity=TrigramSimilarity('name', query),
        ).filter(similarity__gt=0.2).order_by('-similarity')

        filter_form = FilterForm(request.GET)

        authors_set = set(
            [book.author for book in results])
        genre_set = set(
            [genre for book in results for genre in book.genres])
        # authors_arr = [(1, 1) for a]
        authors_choices_list = [(author, author)
                                for author in authors_set]
        genre_choices_list = [(genre, genre)for genre in genre_set]

        authors_choices_list = sorted(authors_choices_list, key=lambda x: x[1])
        genre_choices_list = sorted(genre_choices_list, key=lambda x: x[1])

        filter_form.fields['authors'].choices = authors_choices_list
        filter_form.fields['genre'].choices = genre_choices_list

        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            genres = filter_form.cleaned_data['genre']
            print(genres)
            if results != []:
                results = results.filter(genres__contains=genres)
            else:
                results = Book.objects.filter(genres__contains=genres)

    # if 'price_from' in request.GET:
    #     form = SearchForm(request.GET)
    #     filter_form = FilterForm(request.GET)
    #     sort_form = SortForm(request.GET)
    #     # search_form = SearchForm()
    #     if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
    #         query = form.cleaned_data['query']
    #         price_from = filter_form.cleaned_data['price_from']
    #         if results != []:
    #             results = results.filter(min_price__gt=price_from)
    #         else:
    #             results = Book.objects.filter(min_price__gt=price_from)

    # if 'price_to' in request.GET:
    #     form = SearchForm(request.GET)
    #     filter_form = FilterForm(request.GET)
    #     sort_form = SortForm(request.GET)
    #     # search_form = SearchForm()
    #     if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
    #         query = form.cleaned_data['query']
    #         price_to = filter_form.cleaned_data['price_to']
    #         if results != []:
    #             results = results.filter(min_price__lt=price_to)
    #         else:
    #             results = Book.objects.filter(min_price__lt=price_to)

    if 'more_than_four' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            more_than_four = filter_form.cleaned_data['more_than_four']
            if results != []:
                if more_than_four:
                    results = results.filter(avg_rating__gt=4)
            else:
                if more_than_four:
                    results = Book.objects.filter(avg_rating__gt=4)

    if 'have_electronic' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            have_electronic = filter_form.cleaned_data['have_electronic']
            if results != []:
                if have_electronic:
                    results = results.filter(have_electronic_version=True)
            else:
                if have_electronic:
                    results = Book.objects.filter(have_electronic_version=True)

    if 'have_physical' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            have_physical = filter_form.cleaned_data['have_physical']
            if results != []:
                if have_physical:
                    results = results.filter(have_physical_version=True)
            else:
                if have_physical:
                    results = Book.objects.filter(have_physical_version=True)

    if 'sort' in request.GET:
        # form = SearchForm(request.GET)
        # filter_form = FilterForm(request.GET)
        # sort_form = SortForm(request.GET)
        # search_form = SearchForm()
        if form.is_valid() and filter_form.is_valid() and sort_form.is_valid():
            query = form.cleaned_data['query']
            sort = sort_form.cleaned_data['sort']
            print(sort)
            if results != []:
                if sort == 'default':
                    results = results.annotate(
                        similarity=TrigramSimilarity('name', query),
                    ).filter(similarity__gt=0.2).order_by('-similarity')
                elif sort == 'increase_price':
                    results = results.order_by('min_price')
                elif sort == 'decrease_price':
                    results = results.order_by('-min_price')
            else:
                if have_physical:
                    results = Book.objects.filter(have_physical_version=True)
    html = render(request, 'book_aggregator/search.html', context={
        'form': form,
        'filter_form': filter_form,
        'sort_form': sort_form,
        'query': query,
        # 'authors': authors,
        'books': results
    })
    if 'query' in request.GET:
        html.set_cookie('query', query)
    if 'sort' in request.GET:
        html.set_cookie('sort', sort)
    if request.COOKIES.get('query') is not None:
        print('COOKIE', request.COOKIES.get('query'))
    return html


def book_detail(request, book_slug):
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    added_to_favourite = None

    if request.method == 'POST':
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            if not len(user.favourite_books.filter(id=book.id)):
                user.favourite_books.add(book)
                print('Добавлена')
            else:
                user.favourite_books.remove(book)
        return HttpResponseRedirect(reverse('book_aggregator:detail', args=[book_slug]))

    if request.user.is_authenticated:
        user = get_object_or_404(User, id=request.user.id)
        if not len(user.favourite_books.filter(id=book.id)):
            added_to_favourite = False
        else:
            added_to_favourite = True

    comments = Comment.objects.filter(book=book)
    have_comment = False
    user_comment = None
    print(comments)
    if len(comments.filter(name=request.user.username)):
        have_comment = True

    avg_rating = 0
    if len(comments):
        for comment in comments:
            avg_rating += Rating.objects.get(comment=comment).star.value
        avg_rating /= len(comments)
    print(avg_rating)

    comments_with_rating = []
    for comment in comments:
        rating_for_comment = Rating.objects.get(comment=comment)
        stars_active = rating_for_comment.star.value
        stars_disable = 5 - stars_active
        comments_with_rating.append(
            (rating_for_comment, list(range(stars_active)), list(range(stars_disable)), comment))

    print(have_comment)
    book_sources_list = []
    book_sources = book.sources
    for source in book_sources:
        source_name = ''
        if len(book_sources[source]) != 0:
            if book_sources[source][0]['url'] != '':
                if source == 'litres':
                    source_name = 'Литрес'
                elif source == 'mybook':
                    source_name = 'Mybook'
                elif source == 'labirint':
                    source_name = 'Лабиринт'
                elif source == 'chitai-gorod':
                    source_name = 'Читай Город'
                book_sources_list.append((source_name, book_sources[source]))

    book_genres = book.genres
    similar_books_list = []
    similar_books = Book.objects.filter(
        genres__overlap=book_genres).exclude(slug=book_slug)
    for similar_book in similar_books:
        for genre in similar_book.genres:
            if genre in book_genres:
                similar_books_list.append(similar_book)

    similar_books_dict = {}
    for similar_book in similar_books_list:
        counter = 0
        if similar_book not in similar_books_dict.keys():
            counter += 1
            similar_books_dict[similar_book] = counter
        else:
            similar_books_dict[similar_book] += 1
    sorted_similar_books = sorted(
        similar_books_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_similar_books = [similar_book_item[0]
                            for similar_book_item in sorted_similar_books]
    genres = []
    for genre in book.genres:
        genres.append(SubCategory.objects.get(name=genre))

    print(comments_with_rating)
    return render(request, 'book_aggregator/detail.html', context={
        # 'book_form': book_form,
        'book': book,
        'genres': genres,
        'sources': book_sources_list,
        'similar_books': sorted_similar_books[:9],
        'added_to_favourite': added_to_favourite,
        'comments': comments_with_rating,
        'have_comment': have_comment,
        'avg_rating': avg_rating,
    })


def book_comment(request, book_slug):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))
    have_comment = None

    book = get_object_or_404(Book, slug=book_slug)
    comment = None
    comment_book = request.POST.copy()
    form = CommentForm()

    comments = Comment.objects.filter(book=book)

    if request.user.is_authenticated:
        comment_book['name'] = request.user.username
        comment_book['email'] = request.user.email

        if len(comments.filter(name=request.user.username)):
            user_comment = comments.get(name=request.user.username)
            print(user_comment)
            comment_book['body'] = user_comment.body
            have_comment = True

    print(comment_book)
    form = CommentForm(comment_book)
    rating_form = RatingForm(comment_book)
    print(form.errors)
    if form.is_valid() and rating_form.is_valid() and 'csrfmiddlewaretoken' in request.POST:
        if 'comment_add' in request.POST:
            Comment.objects.update_or_create(
                name=comment_book['name'],
                book=book,
                email=comment_book['email'],
                defaults={'body': request.POST['body']}
            )
            comment = Comment.objects.get(name=comment_book['name'], book=book)
            star = 5
            if 'star' in request.POST:
                try:
                    star = Rating.objects.get(
                        book=book,
                        user=request.user
                    )
                    if star != int(request.POST.get('star')):
                        star = int(request.POST.get('star'))
                except ObjectDoesNotExist:
                    star = int(request.POST.get('star'))
            Rating.objects.update_or_create(
                defaults={'star_id': star},
                book=book,
                user=request.user,
                comment=comment,
            )
            print(comment)
            print(request.POST)
        elif 'comment_delete' in request.POST:
            Comment.objects.get(
                name=comment_book['name'],
                book=book
            ).delete()
        return HttpResponseRedirect(reverse('book_aggregator:detail', args=[book_slug]))
    return render(request, 'book_aggregator/comment.html', context={
        'book': book,
        'form': form,
        'rating_form': rating_form,
        'have_comment': have_comment,
    })


def user_favourite_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    favourite_books = []
    if request.user.is_authenticated:
        favourite_books = request.user.favourite_books.filter()
        commented_books = [comment.book for comment in Comment.objects.filter(
            name=request.user.username)]
        print(commented_books)
    return render(request, 'book_aggregator/favourite_books.html', context={
        'favourite_books': favourite_books,
    })
