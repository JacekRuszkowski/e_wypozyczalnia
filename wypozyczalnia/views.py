from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Category, OrderItem, Order, Review
from .forms import BookForm, ReviewForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, ProtectedError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator


def home(request):
    categories = Category.objects.all()
    paginator = Paginator(Book.objects.all().order_by('title'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    books = page_obj  # wyświetlanie książek z podziałem na strony
    context = {
        'categories': categories,
        'books': books,
    }
    return render(request, 'wypozyczalnia/home-page.html', context)


def search_results(request):
    categories = Category.objects.all()
    query = request.GET.get('q')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )
    context = {
        'categories': categories,
        'books': books
    }
    return render(request, 'wypozyczalnia/search_results.html', context)


def category(request, slug):
    category = Category.objects.get(slug=slug)
    categories = Category.objects.all()
    books = Book.objects.filter(category=category)
    context = {'category': category,
               'books': books,
               'categories': categories,
               }
    return render(request, 'wypozyczalnia/category_view.html', context)


def books_by_author(request, author):
    categories = Category.objects.all()
    books = Book.objects.filter(author=author)
    author_name = author
    content = {
        'books': books,
        'categories': categories,
        'author_name': author_name,
    }
    return render(request, 'wypozyczalnia/author.html', content)


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    categories = Category.objects.all()
    reviews = Review.objects.all()
    user = request.user
    content = {'book': book,
               'categories': categories,
               'reviews': reviews,
               'user': user, }
    return render(request, 'wypozyczalnia/book_detail.html', content)


# funkcje administaratora
# warunek zamiast dekoratora user_passes_test
@user_passes_test(lambda u: u.is_superuser)
def book_add(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, 'Dodano nową książkę')
        return redirect('book-detail', slug=book.slug)
    else:
        form = BookForm()
    content = {'form': form, 'categories': categories}
    return render(request, 'wypozyczalnia/book_edit.html', content)


@user_passes_test(lambda u: u.is_superuser)
def book_edit(request, slug):
    book = get_object_or_404(Book, slug=slug)
    categories = Category.objects.all()
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zmiany zapisane')
            return redirect('book-detail', slug=book.slug)
    else:
        form = BookForm(instance=book)
    content = {'form': form, 'categories': categories}
    return render(request, 'wypozyczalnia/book_edit.html', content)


@user_passes_test(lambda u: u.is_superuser)
def book_delete(request, slug):
    book = get_object_or_404(Book, slug=slug)
    categories = Category.objects.all()
    if request.method == "POST":
        book.delete()
        messages.success(request, f'Książka usunięta')
        return redirect('home')
    content = {'book': book,
               'categories': categories}
    return render(request, 'wypozyczalnia/book_delete.html', content)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Book, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    # order query set
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.warning(
                request, f'Możesz wyporzyczyć tylko jeden egzeplarz danej ksiazki.')
            return redirect('book-detail', slug=item.slug)
        elif order.items.count() == 3:
            messages.warning(
                request, f"W koszyku masz już 3 książki. Nie możesz wypożyczyć więcej.")
            return redirect('book-detail', slug=item.slug)
        else:
            order.items.add(order_item)
            messages.info(request, f'Książka Wypożyczona.')
            return redirect('book-detail', slug=item.slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        # skąd się wzięło tutaj "items"? bo to jest słownik?
        order.items.add(order_item)
        messages.info(request, f'Książka dodana do koszyka.')
        return redirect("book-detail", slug=item.slug)


# logika wypożyczania
@login_required
def borrow_book(request, slug):
    item = get_object_or_404(Book, slug=slug)
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.filter(user=request.user)[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.warning(
                request, f'Możesz wypożyczyć tylko jeden egzemplarz danej książki.')
            return redirect('book-detail', slug=item.slug)
        else:
            if item.copies > 0:
                item.copies -= 1
                item.save()
                order_item, created = OrderItem.objects.get_or_create(
                    item=item,
                    user=request.user,
                    ordered_date=timezone.now(),
                    ordered=False)
                order_item.ordered = True
                order_item.save()
                order.items.add(order_item)
                messages.success(request, f'Książka wypożyczona.')
                return redirect('book-detail', slug=item.slug)
            else:
                messages.warning(request, f'Książka niedostępna.')
                return redirect('book-detail', slug=item.slug)
    else:
        if item.copies > 0:
            item.copies -= 1
            item.save()
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered_date=timezone.now(),
                ordered=False)
            order = Order.objects.create(
                user=request.user, ordered_date=timezone.now())
            order_item.ordered = True
            order_item.save()
            order.items.add(order_item)
            messages.success(request, f'Książka wypożyczona.')
            return redirect('book-detail', slug=item.slug)


@login_required
def return_book(request, slug):
    order = Order.objects.get(user=request.user, ordered=False)
    item = get_object_or_404(Book, slug=slug)
    if order.items.filter(item__slug=item.slug).exists():
        item.copies += 1
        item.save()
        order_item = order.items.filter(item__slug=item.slug)[0]
        order_item.ordered = False
        order_item.return_date = timezone.now()
        order_item.save()
        order.items.remove(order_item)
        messages.success(request, f'Książka zwrócona!')
        # if Review.objects.filter(review_author=request.user, review_book=item).exists():
        #     return redirect('borrows')
        # else:
        return redirect('add-review', slug=item.slug)


@login_required
def borrows(request):
    order_qs = Order.objects.filter(user=request.user)
    time_now = timezone.now()
    if order_qs.exists():
        order = order_qs[0]
        items = order.items.all()
        return render(request, 'wypozyczalnia/cart_test.html', {'items': items, 'time_now': time_now})
    else:
        return render(request, 'wypozyczalnia/cart_test.html')


# dodawanie recenzji
@login_required
def add_review(request, slug):
    book = get_object_or_404(Book, slug=slug)
    # warunek, żeby uzytkownik nie dodał recenzji do książki, której nigdy nie wypożyczył
    # czy to dobre miejsce na ten warunek?
    if not OrderItem.objects.filter(user=request.user, item=book).exists():
        messages.warning(
            request, f'Nie możesz recenzować książki, która nie była przez Ciebie wypożyczona.')
        return redirect('book-detail', book.slug)
    if request.method == "POST":
        # sprawdzanie czy jest recenzja tego użytkownika do tej książki
        # jeśli jest to może ją edytować
        if Review.objects.filter(review_author=request.user, review_book=book).exists():
            review = Review.objects.filter(
                review_author=request.user, review_book=book)[0]
            form = ReviewForm(request.POST, instance=review)
        # jesli nie to może stworzyć nową
        else:
            form = ReviewForm(request.POST)
        instance = form.save(commit=False)
        instance.review_author = request.user
        instance.review_book = book
        if instance.rating > 5 or instance.rating < 1:
            messages.warning(request, f'Ocena musi być od 1 do 5')
            return render(request, 'wypozyczalnia/review_form.html', {'form': form})
        instance.save()
        messages.info(request, f'Dodano recenzję')
        return redirect('book-detail', slug=slug)
    else:
        if Review.objects.filter(review_author=request.user, review_book=book).exists():
            review = Review.objects.filter(
                review_author=request.user, review_book=book)[0]
            form = ReviewForm(instance=review)
        else:
            form = ReviewForm()
    return render(request, 'wypozyczalnia/review_form.html', {'form': form})
