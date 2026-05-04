from django import forms
from .models import Book, BookReview, Borrow

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'genre': forms.Select(),
        }


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment']


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['name', 'date_borrowed']
        widgets = {
            'date_borrowed': forms.DateInput(attrs={'type': 'date'}),
        }
