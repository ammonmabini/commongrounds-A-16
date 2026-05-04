from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('books/', BookListView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailView.as_view(), name='book'),
    path('book/add', BookCreateView.as_view(), name='add'),
    path('book/<int:pk>/edit', BookUpdateView.as_view(), name='edit'),
    path('book/<int:pk>/borrow', BookBorrowView.as_view(), name='borrow'),
    path('book/<int:pk>/bookmark', BookmarkView.as_view(), name='bookmark'),
]

app_name = "bookclub"
