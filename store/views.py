from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum
from django.views.decorators.http import require_POST
from .models import Category, Product, Cart, CartItem, Order, OrderItem

# Home View
def home(request):
    featured_products = Product.objects.filter(badge__in=['new', 'bestseller'])[:6]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


# Product Listing View
def products(request):
    all_products = Product.objects.all()
    categories = Category.objects.all()
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        all_products = all_products.filter(category__id=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)
    
    context = {
        'products': all_products,
        'categories': categories,
        'selected_category': category,
        'search': search,
    }
    return render(request, 'store/products.html', context)


# Product Details View
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


# Add to Cart View
@require_POST
@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity', 1))
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')


# Cart View
@login_required(login_url='login')
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
    
    context = {'cart': cart}
    return render(request, 'store/cart.html', context)


# Update Cart Item
@require_POST
@login_required(login_url='login')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated')
    
    return redirect('cart')


# Remove from Cart
@require_POST
@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart')


# Checkout View
@login_required(login_url='login')
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty')
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        # Create order
        total_amount = cart.total_price
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            total_amount=total_amount,
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.discounted_price,
            )
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation', order_id=order.id)
    
    context = {'cart': cart}
    return render(request, 'store/checkout.html', context)


# Order Confirmation View
@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_confirmation.html', context)


# Order History View
@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders}
    return render(request, 'store/order_history.html', context)


# Order Details View
@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)


# User Registration View
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Cart.objects.create(user=user)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'store/register.html')


# User Login View
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'store/login.html')


# User Logout View
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


# Profile View
@login_required(login_url='login')
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user)

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    total_revenue = Order.objects.aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0

    context = {
        'user': user,
        'orders': orders,

        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
    }

    return render(request, 'store/profile.html', context)


# Category Views
def women_category(request):
    all_products = Product.objects.filter(category__name__icontains='women')
    search = request.GET.get('search', '')
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)
    
    context = {
        'products': all_products,
        'category_name': 'Women',
        'category_emoji': '👩‍🦱',
        'search': search,
    }
    return render(request, 'store/category_products.html', context)


def men_category(request):
    all_products = Product.objects.filter(category__name__icontains='men')
    search = request.GET.get('search', '')
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)
    
    context = {
        'products': all_products,
        'category_name': 'Men',
        'category_emoji': '👨‍💼',
        'search': search,
    }
    return render(request, 'store/category_products.html', context)


def shoes_category(request):
    all_products = Product.objects.filter(category__name__icontains='shoe')
    search = request.GET.get('search', '')
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)
    
    context = {
        'products': all_products,
        'category_name': 'Shoes',
        'category_emoji': '👟',
        'search': search,
    }
    return render(request, 'store/category_products.html', context)


def accessories_category(request):
    all_products = Product.objects.filter(category__name__icontains='accessories')
    search = request.GET.get('search', '')
    if search:
        all_products = all_products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)
    
    context = {
        'products': all_products,
        'category_name': 'Accessories',
        'category_emoji': '👜',
        'search': search,
    }
    return render(request, 'store/category_products.html', context)
    
    from django.db.models import Sum
from django.contrib.auth.models import User

@login_required(login_url='login')
def analytics_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    total_revenue = (
        Order.objects.aggregate(Sum('total_amount'))['total_amount__sum']
        or 0
    )

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
    }

    return render(
        request,
        'store/analytics_dashboard.html',
        context
    )

