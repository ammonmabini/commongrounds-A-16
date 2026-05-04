import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Genre, Book, BookReview, Bookmark, Borrow
from .forms import BookForm, BookReviewForm, BorrowForm
from accounts.models import Profile

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin


def index(request):
    return HttpResponse(
        'Hello World! This came from the index view of the BookClub class')


class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['review_form'] = BookReviewForm()
        context['reviews'] = book.reviews.all()
        context['bookmark_count'] = book.bookmarks.count()

        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            is_bookmarked = book.bookmarks.filter(profile=profile).exists()
            is_borrowed = book.borrowers.filter(borrower=profile).exists()
            borrow = book.borrowers.filter(borrower=profile).first()
            context['is_contributor'] = book.contributor == profile
            context['is_bookmarked'] = is_bookmarked
            context['is_borrowed'] = is_borrowed
            context['borrow'] = borrow

        return context

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        form = BookReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book

            if request.user.is_authenticated:
                review.user_reviewer = request.user.profile
            else:
                review.anon_reviewer = 'Anonymous'

            review.save()
            return redirect('bookclub:book', pk=book.pk)

        context = self.get_context_data()
        context['review_form'] = form
        return render(request, self.template_name, context)


class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_books = Book.objects.all()

        if self.request.user.is_authenticated:
            profile = self.request.user.profile

            contributed = all_books.filter(contributor=profile)
            bookmarked = all_books.filter(bookmarks__profile=profile)
            reviewed = all_books.filter(reviews__user_reviewer=profile)
            remaining_books = all_books.exclude(
                contributor=profile).exclude(
                bookmarks__profile=profile).exclude(
                reviews__user_reviewer=profile)
            
            context['contributed_books'] = contributed
            context['bookmarked_books'] = bookmarked
            context['reviewed_books'] = reviewed
            context['all_books'] = remaining_books
        else:
            context['all_books'] = all_books

        return context

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'bookclub/book_form.html'

    def get(self, request, *args, **kwargs):
        if request.user.profile.role != Profile.ROLE_BOOK_CONTRIBUTOR:
            return redirect('bookclub:books')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].fields['contributor'].disabled = True
        return context

    def post(self, request, *args, **kwargs):
        if request.user.profile.role != Profile.ROLE_BOOK_CONTRIBUTOR:
            return redirect('bookclub:books')

        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.contributor = request.user.profile
            book.save()
            return redirect('bookclub:book', pk=book.pk)

        return render(request, self.template_name, {'form': form})


class BookmarkView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookclub/book.html'

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        profile = request.user.profile

        if Bookmark.objects.filter(profile=profile, book=book).exists():
            Bookmark.objects.filter(profile=profile, book=book).first().delete()
        else:
            bookmark = Bookmark()
            bookmark.profile = profile
            bookmark.book = book
            bookmark.date_bookmarked = datetime.date.today()
            bookmark.save()

        return redirect('bookclub:book', pk=book.pk)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'bookclub/book_form.html'

    def get(self, request, *args, **kwargs):
        if request.user.profile.role != Profile.ROLE_BOOK_CONTRIBUTOR:
            return redirect('bookclub:books')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].fields['contributor'].disabled = True
        return context

    def post(self, request, *args, **kwargs):
        if request.user.profile.role != Profile.ROLE_BOOK_CONTRIBUTOR:
            return redirect('bookclub:books')

        book = self.get_object()
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            return redirect('bookclub:book', pk=book.pk)

        return render(request, self.template_name, {'form': form})

class BookBorrowView(FormView):
    template_name = 'bookclub/book_borrow.html'
    form_class = BorrowForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['name'] = self.request.user.profile.display_name
        return initial

    def post(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        form = BorrowForm(request.POST)

        if form.is_valid():
            two_weeks = datetime.timedelta(weeks=2)
            borrow = form.save(commit=False)
            borrow.book = book
            borrow.date_to_return = borrow.date_borrowed + two_weeks

            if request.user.is_authenticated:
                borrow.borrower = request.user.profile

            borrow.save()
            return redirect('bookclub:book', pk=book.pk)

        context = self.get_context_data()
        context['form'] = form
        return render(request,self.template_name, context)
