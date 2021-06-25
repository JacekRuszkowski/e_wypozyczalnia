from django import forms
from .models import Book, Review


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        Book.slug = Book.title
        fields = ['title', 'author', 'description',
                  'image', 'copies', 'category', 'slug']


class SearchForm(forms.ModelForm):
    q = forms.CharField(label="Szukaj...", max_length=30)


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'review_content', ]
