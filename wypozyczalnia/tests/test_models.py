from django.test import TestCase
from django.core.exceptions import FieldDoesNotExist
from ..models import Book, Category, Order, OrderItem, Review
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import ProtectedError


# ////////////////// sprawdzanie modelu kategorii //////////////////
class CategoryModelTest(TestCase):

    def setUp(self):
        Category.objects.create(name='category1', slug='category1')

    def test_name_label(self):
        category = Category.objects.first()
        field_label = category._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_slug_label(self):
        category = Category.objects.first()
        field_label = category._meta.get_field('slug').verbose_name
        self.assertEqual(field_label, 'slug')

    def test_created_name(self):
        category = Category.objects.first()
        self.assertEqual(category.name, 'category1')


# ///////////////// sprawdzanie modelu książki //////////////////////
class BookModelTest(TestCase):

    def setUp(self):
        category1 = Category.objects.create(name='category1', slug='category1')
        Book.objects.create(title='book1',
                            author='author1',
                            description='description1',
                            pages=2,
                            copies=2,
                            category=category1,
                            slug='book1', )

    def test_category_lebel(self):
        book = Book.objects.first()
        field_label = book._meta.get_field('category').verbose_name
        self.assertEqual(field_label, 'category')

    def test_book_category_constraint(self):
        category = Category.objects.get(id=1)
        book = Book.objects.get(id=1)
        self.assertEqual(category.id, book.category.id)

    def test_book_desription_max_length(self):
        book = Book.objects.first()
        max_length = book._meta.get_field('description').max_length
        self.assertEqual(max_length, None)

    def test_book_title_max_length(self):
        book = Book.objects.first()
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_book_copies_is_PostiveSmallIntegerField(self):
        book = Book.objects.get(id=1)
        field_type = book._meta.get_field('copies').get_internal_type()
        self.assertEqual(field_type, 'PositiveSmallIntegerField')

# //////////////// sprawdzanie czy działa on_delete=PROTECT /////////////////////
    def test_cant_delete_category_when_assigned_to_book(self):
        try:
            Category.objects.get(name='category1').delete()
        except ProtectedError:
            pass
        self.assertEqual(Category.objects.filter(
            name='category1').exists(), True)

    def test_delete_category_when_book_is_deleted(self):
        category = Category.objects.get(name='category1')
        Book.objects.get(category=category).delete()
        category.delete()
        self.assertEqual(Category.objects.filter(
            name='category1').exists(), False)


# sprawdzanie modelu zamówienia
class OrderModelTest(TestCase):

    def setUp(self):
        User.objects.create(username='testuser1', email='testuser1@email.com')
        Category.objects.create(name='category1', slug='category1')
        Book.objects.create(title='book1',
                            author='author1',
                            description='description1',
                            pages=2,
                            copies=2,
                            category=Category.objects.first(),
                            slug='book1', )
        OrderItem.objects.create(user=User.objects.first(
        ), ordered_date=timezone.now(), item=Book.objects.first())
        Order.objects.create(user=User.objects.first(),
                             ordered_date=timezone.now())

    def test_Order_Item_book_constraint(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEqual(order_item.item, Book.objects.first())

    def test_Order_Item_default_ordered_value(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEqual(order_item.ordered, False)

    def test_Order_constraint(self):
        self.assertEqual(Order.objects.first().user, User.objects.first())

    def test_Order_MamyToManyField(self):
        field_type = Order.objects.first()._meta.get_field('items').get_internal_type()
        self.assertEqual(field_type, 'ManyToManyField')

# /////////////  sprawdzanie czy po usunięciu usera usunięte zostanie jego zamwówienie /////////////////
    def test_user_delete_deletes_his_order(self):
        User.objects.first().delete()
        self.assertEqual(Order.objects.first(), None)
