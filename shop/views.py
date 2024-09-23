from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ContactForm, CustomUserCreationForm, CustomAuthenticationForm
from .models import Category, Product
from cart.forms import CartAddProductForm
# Create your views here.


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category': category, 'categories': categories, 'products': products})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('shop:product_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('shop:product_list')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('shop:product_list')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Handle form submission
            return redirect('shop:product_list')
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form})

def about(request):
    return render(request, 'shop/about.html')