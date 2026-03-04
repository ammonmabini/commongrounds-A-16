from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('books/', BookListView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailView.as_view(), name='book'),
]

app_name = "bookclub"
