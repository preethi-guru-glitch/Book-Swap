from time import timezone
import datetime
from django.shortcuts import render
from datetime import timedelta
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, BorrowRecord
from .forms import BookSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import CustomUserCreationForm  # You'll need to create this

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # Make sure 'profile' is a valid URL name
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def index(request):
    form = BookSearchForm(request.GET or None)
    books = Book.objects.filter(available=True)

    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        books = books.filter(title__icontains=search_query)

    return render(request, 'index.html', {
        'books': books,
        'form': form
    })


@login_required
def profile(request):
    current_borrows = BorrowRecord.objects.filter(
        user=request.user,
        returned=False
    )
    past_borrows = BorrowRecord.objects.filter(
        user=request.user,
        returned=True
    )[:10]

    return render(request, 'profile.html', {
        'current_borrows': current_borrows,
        'past_borrows': past_borrows
    })


@login_required
def borrow_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if book.available:
        BorrowRecord.objects.create(
            user=request.user,
            book=book,
            return_date=timezone.now() + timezone.timedelta(days=14)
        )
        book.available = False
        book.save()
    return redirect('profile')


def ebooks(request):
    ebooks = Book.objects.filter(book_type='EBOOK')
    return render(request, 'ebooks.html', {'ebooks': ebooks})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, BorrowRecord, Category
from .forms import BookForm, CategoryForm

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            form.save_m2m()  # For many-to-many relationships
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

def book_list(request):
    books = Book.objects.filter(available=True)
    return render(request, 'book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    is_borrowed = False
    if request.user.is_authenticated:
        is_borrowed = BorrowRecord.objects.filter(
            book=book,
            user=request.user,
            returned=False
        ).exists()
    return render(request, 'book_details.html', {
        'book': book,
        'is_borrowed': is_borrowed
    })

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.available:
        BorrowRecord.objects.create(
            book=book,
            user=request.user,
            return_date=timezone.now() + timezone.timedelta(days=14)
        )
        book.available = False
        book.save()
    return redirect('book_detail', pk=pk)

@login_required
def return_book(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk, user=request.user)
    if not record.returned:
        record.returned = True
        record.save()
        record.book.available = True
        record.book.save()
    return redirect('profile')
from django.shortcuts import render
from .models import Book

