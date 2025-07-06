from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Order, OrderItem
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html',{'products':products})

def product_detail(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    return render(request,'product_detail.html',{'product':product})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart_view')

# 🛍 View cart
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

# ❌ Remove from cart
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_view')

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_view')

    total = 0
    order_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        order_items.append((product, quantity, product.price))

    order = Order.objects.create(user=request.user, total=total)

    for product, quantity, price in order_items:
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

    # Clear the cart
    request.session['cart'] = {}

    return render(request, 'order_success.html', {'order': order})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'User registered successfully')
        return redirect('login')
    return render(request, 'register.html')

# 🔐 Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'login.html')

# 🔐 Logout
def logout_view(request):
    logout(request)
    return redirect('home')