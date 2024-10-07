from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import EmptyPage, PageNotAnInteger
from .models import Cart, CartItem, Order, OrderItem, Review
from .forms import CheckoutForm, OrderForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from users.forms import CustomSignupForm
from django.urls import reverse_lazy
from django.views.generic import CreateView


User = get_user_model()


class CustomSignupView(CreateView):
    form_class = CustomSignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):

        user = form.save()
        return super().form_valid(form)


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from .forms import ProductFilterForm, ReviewForm

def product_list(request):
    product_list = Product.objects.all().order_by('id')
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['category']:
            product_list = product_list.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['min_price']:
            product_list = product_list.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price']:
            product_list = product_list.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data['search_query']:
            product_list = product_list.filter(name__icontains=form.cleaned_data['search_query'])

    paginator = Paginator(product_list, 6)  # Измените здесь на 6
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    review_form = ReviewForm()

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'form': form,
        'review_form': review_form,
    })

@login_required
def order_preview(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        delivery_option = request.POST.get('delivery_option')
        payment_option = request.POST.get('payment_option')

        if delivery_option and payment_option:
            order.delivery_option = delivery_option
            order.payment_option = payment_option
            order.update_total_price()
            order.save()

            return redirect('confirm_order', order_id=order.id)

    return render(request, 'products/order_preview.html', {'order': order})



@login_required
async def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            profile = request.user
            order.name = profile.first_name + ' ' + profile.last_name
            order.phone = profile.phone
            order.email = profile.email
            order.telegram_username = profile.telegram_username
            order.save()

            # Формируем сообщение для отправки в Telegram
            message = (
                f"Новый заказ создан!\n"
                f"ID заказа: {order.id}\n"
                f"Имя: {order.name}\n"
                f"Телефон: {order.phone}\n"
                f"Email: {order.email}\n"
                f"Telegram Username: {order.telegram_username}"
            )

            # Отправляем сообщение в Telegram
            from telegram_bot.notifications import send_telegram_message
            await send_telegram_message(profile.chat_id, message)

            return redirect('order_success')
    else:
        form = OrderForm(user=request.user)
    return render(request, 'products/create_order.html', {'form': form})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'products/order_detail.html', {'order': order})

@login_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        print("POST-запрос получен")
        print("Данные формы:", request.POST)

        order.status = 'completed'
        order.save()

        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()

        return redirect('order_detail', order_id=order.id)
    else:
        print("Метод не POST")

    return render(request, 'products/confirm_order.html', {'order': order})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'products/add_review.html', {'form': form, 'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
    })

def orders_report(request):
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()

    total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_price'))
    average_order_value = Order.objects.filter(status='completed').aggregate(Avg('total_price'))

    delivery_stats = Order.objects.values('delivery_option').annotate(count=Count('delivery_option'))
    payment_stats = Order.objects.values('payment_option').annotate(count=Count('payment_option'))

    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue['total_price__sum'],
        'average_order_value': average_order_value['total_price__avg'],
        'delivery_stats': delivery_stats,
        'payment_stats': payment_stats,
    }

    return render(request, 'products/orders_report.html', context)

def order_success(request):
    return render(request, 'products/order_success.html')

def index(request):
    products = Product.objects.all().order_by('id')
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 9)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    form = ReviewForm()

    return render(request, 'products/index.html', {
        'page_obj': page_obj,
        'form': form,
    })

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_price': cart.total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart.update_total_price()
    return redirect('index')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    cart_item.cart.update_total_price()
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                delivery_option=form.cleaned_data['delivery_option'],
                payment_option=form.cleaned_data['payment_option'],
                status='pending'
            )

            for item in cart.items.all():
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            order.update_total_price()
            cart.items.all().delete()
            cart.update_total_price()

            return redirect('order_preview', order_id=order.id)
        else:
            return render(request, 'products/checkout.html', {'form': form, 'cart': cart})
    else:
        form = CheckoutForm()

    return render(request, 'products/checkout.html', {'form': form, 'cart': cart})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'products/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

