from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, View, FormView, TemplateView
from django.contrib.auth.forms import UserCreationForm  # Django's built-in form
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import logout
from .models import User, Product, Restaurant, MenuItem, CartItem, Order, OrderItem
from .forms import ProductForm, CartItemForm, UpdateCartItemForm, OrderForm, CustomUserCreationForm


class HomeView(TemplateView):
    template_name = 'core/home.html'


class MarketView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'core/market.html'
    context_object_name = 'products'
    login_url = 'core:login'  # Django's way to redirect if not logged in

    def get_queryset(self):
        return Product.objects.filter(available=True)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/add_product.html'
    success_url = '/market/'
    login_url = 'core:login'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Product has been added!')
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    next_page = 'core:home'  # Default redirect after successful login

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful!')
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse(self.next_page)

class RegistrationView(FormView):
    template_name = 'core/register.html'
    form_class = CustomUserCreationForm  # Use the custom form
    success_url = '/login/'

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Your account has been created! You can now log in')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, 'Product has been deleted!')
        return redirect('core:admin')

    def test_func(self):
        return self.request.user.is_superuser

'''              
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        if self.request.user.id == user_id:
            messages.error(request, "Cannot delete your own admin account!")
            return redirect('core:admin')

        if target_user.is_superuser:
            messages.error(request, "Cannot delete other admin accounts!")
            return redirect('core:admin')

        # Delete all products owned by the user
        Product.objects.filter(owner_id=user_id).delete()
        target_user.delete()
        messages.success(request, 'User and their products have been deleted!')
        return redirect('core:admin')

    def test_func(self):
        return self.request.user.is_superuser

                             
def admin_panel(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('core:home')
    users = User.objects.all()
    products = Product.objects.all()
    return render_template('admin.html', title='Admin Panel', users=users, products=products)

'''

class BuyProductView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if product.owner == request.user:
            messages.error(request, "You can't buy your own product!")
        elif not product.available:
            messages.error(request, 'This product is no longer available.')
        elif request.user.budget < product.price:
            messages.error(request, 'Not enough money to buy this product!')
        else:
            request.user.budget -= product.price
            product.owner.budget += product.price
            product.owner = request.user
            request.user.save()
            product.owner.save()
            messages.success(request, 'Successfully purchased product!')
            return redirect('core:observe')
        return redirect('core:market')


def observe(request):
    return render(request, 'core/observe.html')


def submit_order(request):
    # Тут можно сохранить заказ, например в базу или лог
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')
    phone_number = request.POST.get('phoneNumber')
    restaurant = request.POST.get('restaurant')
    print(f"Order from {first_name} {last_name} ({phone_number}) for {restaurant}")

    return JsonResponse({'redirect_url': reverse('core:observe')})


def get_positions(request):
    # Это пример. Ты можешь получать данные из модели, БД или модуля.
    drone_data = [{
        "id": "DRONE_001",
        "battery": 85,
        "weather": "Ясно",
        "temp": 22,
        "humidity": 40,
        "wind_speed": 3,
        "gps": [43.1965135, 76.6309754]
    }]
    return JsonResponse(drone_data)


def calculate_eta(request):
    try:
        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))
        # Сюда добавь реальную логику расчета
        eta = 5.3  # в минутах
        return JsonResponse({"eta": eta})
    except Exception as e:
        return JsonResponse({"error": "Ошибка при расчете ETA"}), 400


def create_order(request):
    try:
        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))

        # Получаем товары из корзины
        cart_items = CartItem.objects.filter(user=request.user).all()
        if not cart_items:
            return JsonResponse({"error": "Your cart is empty!"}), 400

        # Создаем заказ
        restaurant = cart_items[0].menu_item.restaurant
        total = sum(item.menu_item.price * item.quantity for item in cart_items)

        order = Order(
            user=request.user,
            restaurant=restaurant,
            total_price=total,
            delivery_latitude=lat,
            delivery_longitude=lon,
            status='created'
        )
        order.save()

        # Создаем элементы заказа
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price_at_time=cart_item.menu_item.price
            )
            order_item.save()

        # Очищаем корзину
        CartItem.objects.filter(user=request.user).delete()

        print(f"Order created: {order.id}")
        return JsonResponse({"order_id": order.id})
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return JsonResponse({"error": "Error creating order"}), 500


def start_drone(request):
    try:
        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))
        order_id = int(request.POST.get('order_id'))

        # Проверяем батарею
        battery_level = 85
        if battery_level < 20:
            return JsonResponse({"error": "Батарея слишком низкая"}), 400

        # Обновляем статус заказа
        order = Order.objects.get(id=order_id)
        if not order:
            return JsonResponse({"error": "Order not found"}), 404

        if order.user != request.user:
            return JsonResponse({"error": "Access denied"}), 403

        order.status = 'in_transit'
        order.save()
        print(f"Order {order.id} status updated to in_transit")

        return JsonResponse({"status": "ok"})
    except Exception as e:
        print(f"Error starting drone: {str(e)}")
        return JsonResponse({"error": "Error starting drone"}), 500


def complete_delivery(request):
    try:
        order_id = request.POST.get('order_id')
        if not order_id:
            print("No order_id provided in request")
            return JsonResponse({'error': 'Order ID is required'}), 400

        order_id = int(order_id)
        order = Order.objects.get(id=order_id)

        # Проверяем, что заказ принадлежит текущему пользователю
        if order.user != request.user:
            return JsonResponse({'error': 'Access denied'}), 403

        # Обновляем статус заказа
        order.status = 'completed'
        order.save()

        print(f"Order {order_id} marked as completed")
        return JsonResponse({'success': True})

    except ValueError:
        print(f"Error completing delivery: invalid order_id format")
        return JsonResponse({'error': 'Invalid order ID format'}), 400
    except Exception as e:
        print(f"Error completing delivery: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}), 500


class RestaurantsView(ListView):
    model = Restaurant
    template_name = 'core/restaurants.html'
    context_object_name = 'restaurants'


class RestaurantMenuView(ListView):
    model = MenuItem
    template_name = 'core/restaurant_menu.html'
    context_object_name = 'menu_items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = get_object_or_404(Restaurant, id=self.kwargs['restaurant_id'])
        context['form'] = CartItemForm()
        return context

    def get_queryset(self):
        self.restaurant = get_object_or_404(Restaurant, id=self.kwargs['restaurant_id'])
        return MenuItem.objects.filter(restaurant=self.restaurant)


class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'core/cart.html'
    context_object_name = 'cart_items'
    login_url = 'core:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        
        # Calculate total
        total = sum(item.menu_item.price * item.quantity for item in cart_items)
        context['total'] = total
        context['update_form'] = UpdateCartItemForm()
        return context

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class AddToCartView(LoginRequiredMixin, View):
    login_url = 'core:login'

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        form = CartItemForm(request.POST)
        if form.is_valid():
            menu_item = get_object_or_404(MenuItem, id=form.cleaned_data['menu_item_id'])
            existing_item = CartItem.objects.filter(
                user=request.user,
                menu_item=menu_item
            ).first()

            if existing_item:
                existing_item.quantity += form.cleaned_data['quantity']
                existing_item.save()
            else:
                cart_item = CartItem(
                    user=request.user,
                    menu_item=menu_item,
                    quantity=form.cleaned_data['quantity']
                )
                cart_item.save()

            messages.success(request, 'Item added to cart!')
        return redirect('core:cart')


class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, cart_item_id):
        form = UpdateCartItemForm(request.POST)
        if form.is_valid():
            cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
            cart_item.quantity = form.cleaned_data['quantity']
            cart_item.save()
            messages.success(request, 'Cart updated!')
        return redirect('core:cart')
    login_url = 'core:login'


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
        return redirect('core:cart')
    login_url = 'core:login'


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'core/checkout.html'
    form_class = OrderForm
    success_url = '/order_confirmation/'
    login_url = 'core:login'

    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, 'Your cart is empty!')
            return redirect('core:cart')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = CartItem.objects.filter(user=self.request.user)
        
        # Calculate subtotal for each item and total
        total = 0
        for item in cart_items:
            item.subtotal = item.menu_item.price * item.quantity
            total += item.subtotal
            
        context['cart_items'] = cart_items
        context['total'] = total
        return context

    def form_valid(self, form):
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items:
            messages.warning(self.request, 'Your cart is empty!')
            return redirect('core:cart')

        # Create order
        restaurant = cart_items[0].menu_item.restaurant
        total = sum(item.menu_item.price * item.quantity for item in cart_items)

        order = Order(
            user=self.request.user,
            restaurant=restaurant,
            total_price=total,
            delivery_latitude=form.cleaned_data['delivery_latitude'],
            delivery_longitude=form.cleaned_data['delivery_longitude']
        )
        order.save()

        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price_at_time=cart_item.menu_item.price
            )
            order_item.save()

        # Clear cart
        CartItem.objects.filter(user=self.request.user).delete()

        messages.success(self.request, 'Order placed successfully!')
        return redirect(reverse('core:order_confirmation', kwargs={'order_id': order.id}))


class OrderConfirmationView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/order_confirmation.html'
    context_object_name = 'order'
    login_url = 'core:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, id=self.kwargs['order_id'])


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders.html'
    context_object_name = 'orders'
    login_url = 'core:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('core:home')

    def post(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('core:home')
