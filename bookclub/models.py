from django.db import models
from django.urls import reverse

class Genre(models.Model): #Should be sorted by name in ascending order
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
    author = models.CharField()
    pubYear = models.IntegerField()
    createdOn = models.DateTimeField(auto_now_add=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookclub:book', kwargs={'pk' : self.pk})

    class Meta:
        ordering = ['-pubYear']
        verbose_name = 'book'
        verbose_name_plural = 'books'
