from django.test import SimpleTestCase
from django.urls import resolve, reverse
from ..views import (home,
                     category,
                     book_edit,
                     book_add,
                     book_delete,
                     book_detail,
                     books_by_author,
                     search_results,
                     return_book,
                     borrows,
                     borrow_book,
                     add_review
                     )


class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_category_url_is_resolved(self):
        url = reverse('categories', args=['slug'])
        self.assertEqual(resolve(url).func, category)

    def test_search_results_url_is_resolved(self):
        url = reverse('search-results')
        self.assertEqual(resolve(url).func, search_results)

    def test_books_by_author_url_is_resolved(self):
        url = reverse('authors-books', args=['slug'])
        self.assertEqual(resolve(url).func, books_by_author)

    def test_book_edit_url_is_resolved(self):
        url = reverse('book-edit', args=['slug'])
        self.assertEqual(resolve(url).func, book_edit)

    def test_book_add_url_is_resolved(self):
        url = reverse('book-add')
        self.assertEqual(resolve(url).func, book_add)

    def test_book_delete_url_is_resolved(self):
        url = reverse('book-delete', args=['slug'])
        self.assertEqual(resolve(url).func, book_delete)

    def test_book_detail_url_is_resolved(self):
        url = reverse('book-detail', args=['slug'])
        self.assertEqual(resolve(url).func, book_detail)

    def test_return_books_url_is_resolved(self):
        url = reverse('return-book', args=['slug'])
        self.assertEqual(resolve(url).func, return_book)

    def test_borrows_url_is_resolved(self):
        url = reverse('borrows')
        self.assertEqual(resolve(url).func, borrows)

    def test_borrow_book_url_is_resolved(self):
        url = reverse('borrow-book', args=['slug'])
        self.assertEqual(resolve(url).func, borrow_book)

    def test_add_review_url_is_resolved(self):
        url = reverse('add-review', args=['slug'])
        self.assertEqual(resolve(url).func, add_review)
