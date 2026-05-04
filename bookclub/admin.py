from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Genre, Book, BookReview, Bookmark, Borrow


class GenreAdmin(admin.ModelAdmin):
    model = Genre


class BookAdmin(admin.ModelAdmin):
    model = Book


class BookReviewAdmin(admin.ModelAdmin):
    model = BookReview


class BookmarkAdmin(admin.ModelAdmin):
    model = Bookmark


class BorrowAdmin(admin.ModelAdmin):
    model = Borrow


admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Borrow, BorrowAdmin)
