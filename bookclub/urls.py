from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    #path('books/', BooksListView.as_view(), name='books'),
    #path('book/<int:pk>', BooksDetailView.as_view(), name='book'),
]

app_name = "bookclub"