from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from users.models import Profile
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


# kategoria
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        unique_together = ('slug',)
        ordering = ('name',)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


# książka
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(default='default.jpg', upload_to='book_images')
    copies = models.PositiveSmallIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# recenzje
class Review(models.Model):
    review_author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_content = models.TextField()
    rating_numbers = (
        (1, '1 - Bardzo słaba'),
        (2, '2 - Słaba'),
        (3, '3 - Średnia'),
        (4, '4 - Dobra'),
        (5, '5 - Bardzo dobra')
    )
    rating = models.IntegerField(choices=rating_numbers, default=1)
    review_date = models.DateTimeField(default=timezone.now)
    review_book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return self.review_content


# logika wypożyczania:
class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField()
    return_date = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=14))
    item = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.item.author} - "{self.item.title}"'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField()
    items = models.ManyToManyField(OrderItem)

    def __str__(self):
        return f'{self.user.username}'
