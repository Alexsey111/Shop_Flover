from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from users.views import SignupView, ActivationView

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('cart/', views.view_cart, name='view_cart'),  # Просмотр корзины
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление в корзину
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Удаление из корзины
    path('checkout/', views.checkout, name='checkout'),  # Оформление заказа
    path('registration/logout/', LogoutView.as_view(template_name='account/logout.html'), name='logout'),
    path('order/success/', views.order_success, name='order_success'),  # Успешное оформление заказа
    path('products/', views.product_list, name='product_list'),  # Список продуктов
    path('order/preview/<int:order_id>/', views.order_preview, name='order_preview'),  # Предварительный просмотр заказа
    path('order/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),  # Подтверждение заказа
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),  # Детали заказа
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Детали продукта
    path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),  # Добавление отзыва
    path('orders_report/', views.orders_report, name='orders_report'),  # Отчет по заказам
]







# urlpatterns = [
#     path('', views.index, name='index'),  # Главная страница
#     path('cart/', views.view_cart, name='view_cart'),  # Просмотр корзины
#     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление в корзину
#     path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Удаление из корзины
#     path('checkout/', views.checkout, name='checkout'),  # Оформление заказа
#     path('login/', views.login_view, name='account_login'),  # Вход
#     path('logout/', LogoutView.as_view(), name='account_logout'),  # Выход
#     #path('signup/', views.signup_view, name='account_signup'),  # Регистрация
#     path('signup/', CustomSignupView.as_view(), name='account_signup'),
#     path('order/success/', views.order_success, name='order_success'),  # Успешное оформление заказа
#     path('products/', views.product_list, name='product_list'),  # Список продуктов
#     path('order/preview/<int:order_id>/', views.order_preview, name='order_preview'),  # Предварительный просмотр заказа
#     path('order/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),  # Подтверждение заказа
#     path('order/<int:order_id>/', views.order_detail, name='order_detail'),  # Детали заказа
#     path('accounts/logout/', LogoutView.as_view(template_name='account/logout.html'), name='logout'),  # Выход
#     path('accounts/logout/confirm/', LogoutView.as_view(template_name='account/confirm_logout.html'), name='logout_confirmed'),  # Подтверждение выхода
#     path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Детали продукта
#     path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),  # Добавление отзыва
#     path('orders_report/', views.orders_report, name='orders_report'),  # Отчет по заказам
# ]


