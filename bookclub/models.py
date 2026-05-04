from django.db import models
from django.urls import reverse
from accounts.models import Profile


class Genre(models.Model):  # Should be sorted by name in ascending order
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bookclub:book_list', args=[str(self.name)])

    class Meta:
        ordering = ['name']
        verbose_name = 'genre'
        verbose_name_plural = 'genres'


class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        related_name="books",
        null=True,
        blank=True
    )
    contributor = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name='books',
        null=True,
        blank=True,
    )
    author = models.CharField()
    synopsis = models.TextField(null=True, blank=True)
    publication_year = models.IntegerField()
    available_to_borrow = models.BooleanField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookclub:book', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-publication_year']
        verbose_name = 'book'
        verbose_name_plural = 'books'


class BookReview(models.Model):
    user_reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='user_reviews',
        null=True,
        blank=True,
    )
    anon_reviewer = models.TextField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
    )
    title = models.CharField()
    comment = models.TextField()

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        null = True,
        blank = True,
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        null = True,
        blank = True,
    )
    date_bookmarked = models.DateField()


class Borrow(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrowers',
        null = True,
        blank = True,
    )
    borrower = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='borrowed',
        null = True,
        blank = True,
    )
    name = models.CharField()
    date_borrowed = models.DateField()
    date_to_return = models.DateField()
