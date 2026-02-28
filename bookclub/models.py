from django.db import models
from django.urls import reverse

class Genre(models.Model): #Should be sorted by name in ascending order
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return'{}'.format(self.name)
    
    def get_absolute_url(self):
        return reverse('bookclub:book_list', args=[str(self.name)])
    
    class Meta:
        ordering = ['name']
        verbose_name = 'genre'
        verbose_name_plural = 'genres'


class Book(models.Model): #Should be sorted by the date it was published in descending order
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name="books"
    )
    author = models.CharField()
    pubYear = models.IntegerField()
    createdOn = models.DateTimeField(auto_now_add=True) #only gets set when the model is created
    updatedOn = models.DateTimeField(auto_now=True) #always updated on the last model update

    def __str__(self):
        return'{}'.format(self.title)
    
    def get_absolute_url(self):
        return reverse('bookclub:book', args=[str(self.pk)])
    
    class Meta:
        ordering = ['pubYear']
        verbose_name = 'book'
        verbose_name_plural = 'books'