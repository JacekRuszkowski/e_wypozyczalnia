from django.test import TestCase, Client
from django.urls import reverse
from ..models import Book, Category, Order, OrderItem, Review
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone
import random


class TestHomeView(TestCase):
    def setUp(self):
        books = 14
        category1 = Category.objects.create(name='category1',
                                            slug='category1', )
        for book_number in range(books):
            Book.objects.create(title=f'book1 {book_number}',
                                author=f'author1 {book_number}',
                                description='description1',
                                pages=2,
                                category=category1,
                                slug=f'book1 {book_number}', )

    def test_books_are_created(self):
        books = Book.objects.all()
        self.assertEqual(books.count(), 14)

    # //////////// sprawdzanie czy ścieżka url istnieje ///////////////
    def test_url_exists(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    # //////////// sprawdzanie czy nazwa url jest poprawna ///////////////
    def test_acces_to_url_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    # //////////// sprawdzanie czy wyświetla poprawny template html  ///////////////
    def test_home_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'wypozyczalnia/base.html')

    # //////////// sprawdzanie czy jest paginacja  ///////////////
    # ile jest książek na pierwszej i drugiej stronie
    def test_pagination_first_page(self):
        response = self.client.get(reverse('home'))
        self.assertTrue(len(response.context['books']) == 8)

    def test_pagination_second_page(self):
        response = self.client.get(reverse('home') + '?page=2')
        self.assertTrue(len(response.context['books']) == 6)

    # /////////////////// wyszukiwanie //////////////////
    def test_search_results(self):
        self.assertQuerysetEqual(Book.objects.filter(
            title__icontains='book1 0'), ['<Book: book1 0>'])


# /////////////////// testowanie widoku kategorii ///////////
class TestCategoryAndAuthorView(TestCase):
    def setUp(self):
        categories = 5
        books = 15
        # tworzę 5 kategorii
        for category_number in range(categories):
            Category.objects.create(name=f'category{category_number}',
                                    slug=f'category{category_number}')
        # twrzę 15 książek i przypisuje do nich stworzone kategorie
        number = 0
        for book_number in range(books):
            category = Category.objects.all()[number]
            Book.objects.create(title=f'book{book_number}',
                                author=f'author{book_number}',
                                description='description1',
                                pages=2,
                                category=category,
                                slug=f'book{book_number}')
            number += 1
            if number > 4:
                number = 0

        self.category = Category.objects.first()
        self.book = Book.objects.first()

    def test_books_category_created_correctly(self):
        books = Book.objects.filter(category=self.category)
        self.assertEqual(books.count(), 3)

    def test_category_view_correct_template(self):
        response = self.client.get(
            reverse('categories', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wypozyczalnia/category_view.html')

    # sprawdzam czy wyświetla sie właściwa iilosc książek dla danej kategorii
    def test_category_view_context(self):
        response = self.client.get(
            reverse('categories', kwargs={'slug': self.category.slug}))
        self.assertTrue('category' in response.context)
        self.assertTrue('books' in response.context)
        self.assertEqual(response.context['books'].count(), 3)

    # widok autora książek
    def test_author_view_correct_template(self):
        response = self.client.get(
            reverse('authors-books', args=[self.book.author]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wypozyczalnia/author.html')

    def test_author_view_context(self):
        response = self.client.get(
            reverse('authors-books', args=[self.book.author]))
        self.assertEqual(response.context['books'].count(), 1)


# /////////////////// zalogowany użytkownik //////////////////
class TestLoginLogic(TestCase):
    def setUp(self):
        # tworzenie użytkownika
        testuser1 = User.objects.create_user(
            username='testuser1', email='testuser1@mail.com', password='Haslo123')
        testuser2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='Haslo123')
        admin = User.objects.create_superuser(
            username='superuser1', email='superuser1@mail.com', password='Haslo123')
        # stworzenie ksiażki i kategorii
        category1 = Category.objects.create(name='category1',
                                            slug='category1', )
        self.book1 = Book.objects.create(title='book1',
                                         author='author1',
                                         description='description1',
                                         pages=2,
                                         category=category1,
                                         slug='book1', )
        # stworzenie instancji ksiazki do wypozyczenia
        self.order_item_1 = OrderItem.objects.create(user=testuser1, item=self.book1,
                                                     ordered_date=timezone.now())
        # tworzenie zamówienie
        self.order1 = Order.objects.create(
            user=testuser1, ordered_date=timezone.now())
        self.order1.items.add(self.order_item_1)

    # sprawdzanie czy użtkonik niezalogowany zostanie przekierowany na stronę logowania
    def test_redirect_to_login_when_accessing_borrows(self):
        response = self.client.get(reverse('borrows'))
        self.assertRedirects(response, '/login/?next=/borrows/')

    def test_redirect_to_login_when_trying_to_borrow(self):
        response = self.client.get(
            reverse('borrow-book', args=[self.book1.slug]))
        self.assertTrue(response.url.startswith, '/login/')

    def test_not_logged_user_profile_redirect(self):
        response = self.client.get(reverse('profile-view'))
        self.assertTrue(response.url.startswith, '/login/?next=/profile/')

    # sprawdzanie czy niezalogowany użytkownik ma podgląd profilów innych użytkowników (ma, ale tylko z recenzjami)
    def test_other_users_profile_preview_for_not_logged_user(self):
        testuser2 = User.objects.get(username='testuser2')
        response = self.client.get(
            reverse('profile-preview', args=[testuser2.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_preview.html')

    # zalogowoany user wchodzi na swój profil
    def test_logged_user_see_his_profile(self):
        login = self.client.login(username='testuser1', password='Haslo123')
        response = self.client.get(reverse('profile-view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    # czy uzytkownik widzi swoje wypozyczenia
    def test_user_see_borrowed_books(self):
        login = self.client.login(username='testuser1', password='Haslo123')
        response = self.client.get(reverse('borrows'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('items' in response.context)
        self.assertEqual(response.context['items'].count(), 1)

    # użytkownik widzi historię swoich wypożyczeń
    def test_user_see_hisotory_of_borrows_in_profile_view(self):
        # usunięcie książki z zamówienia
        self.order1.items.remove(self.order_item_1)
        login = self.client.login(username='testuser1', password='Haslo123')
        response = self.client.get(reverse('profile-view'))
        self.assertEqual(response.status_code, 200)
        # sprawdzenie czy książka jest nadal widoczna na stronie użytkownika po oddaniu (usunięciu z zamówienia
        self.assertTrue('order_items' in response.context)
        self.assertEqual(response.context['order_items'].count(), 1)

    # użytkownik może dodać recenzjęc tylko podczas oddania książki
    # nie może recenzować książki, której nie wypożyczał i zwrwaca go na strone książki
    def test_user_cant_review_book_which_wasnt_borrowed(self):
        login = self.client.login(username='testuser1', password='Haslo123')
        test_book = Book.objects.create(title='test_book',
                                        author='test_author',
                                        description='test_discription',
                                        pages=2,
                                        category=Category.objects.first(),
                                        slug='test_book', )
        response = self.client.get(
            reverse('add-review', args=[test_book.slug]))
        self.assertRedirects(response, '/test_book/')

    # //////////////////////////////////// rzeczy admina /////////////////////////////////////////////////////

    # sprawdzanie czy byle kto może usunąć albo dodać książkę
    def test_redirect_to_login_if_not_admin_tries_to_edit_book(self):
        book1 = Book.objects.get(title='book1')
        login = self.client.login(username='testuser1', password='Haslo123')
        response = self.client.get(reverse('book-edit', args=[book1.slug]))
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_login_if_not_admin_tries_to_delete_book(self):
        book1 = Book.objects.get(title='book1')
        login = self.client.login(username='testuser1', password='Haslo123')
        response = self.client.get(reverse('book-delete', args=[book1.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith, '/login/?next=/book1/deete/')

    # sprawdzanie czy admin ma dostęp do powyższych
    def test_book_edit_template(self):
        book1 = Book.objects.get(title='book1')
        self.client.login(username='superuser1', password='Haslo123')
        response = self.client.get(reverse('book-edit', args=[book1.slug]))
        self.assertTemplateUsed(response, 'wypozyczalnia/book_edit.html')

    def test_book_add_template(self):
        self.client.login(username='superuser1', password='Haslo123')
        response = self.client.get(reverse('book-add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wypozyczalnia/book_edit.html')
