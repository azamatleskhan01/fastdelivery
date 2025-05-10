from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('market/', views.MarketView.as_view(), name='market'),
    path('add_product/', views.ProductCreateView.as_view(), name='add_product'),
    path('delete_product/<int:product_id>/', views.ProductDeleteView.as_view(), name='delete_product'),

    path('buy/<int:product_id>/', views.BuyProductView.as_view(), name='buy_product'),
    path('observe/', views.observe, name='observe'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('get_positions/', views.get_positions, name='get_positions'),
    path('calculate_eta/', views.calculate_eta, name='calculate_eta'),
    path('create_order/', views.create_order, name='create_order'),
    path('start_drone/', views.start_drone, name='start_drone'),
    path('complete_delivery/', views.complete_delivery, name='complete_delivery'),
    path('restaurants/', views.RestaurantsView.as_view(), name='restaurants'),
    path('restaurant/<int:restaurant_id>/', views.RestaurantMenuView.as_view(), name='restaurant_menu'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add_to_cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update_cart/<int:cart_item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order_confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('orders/', views.OrdersView.as_view(), name='orders'),
]