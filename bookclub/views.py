from django.shortcuts import render
from django.http import HttpResponse
from .models import Genre, Book

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

def index(request):
    return HttpResponse('Hello World! This came from the index view of the BookClub class')

class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book.html'

class BookListView(ListView):
    model = Genre
    template_name = 'bookclub/book_list.html'
