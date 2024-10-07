from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Product, Order
from users.models import CustomUser

# Регистрация моделей Category, Product и Order
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)

# Кастомный админ для модели CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Настройка полей, отображаемых в админ-панели
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telegram_username', 'phone', 'address', 'chat_id')}),
    )
    # Добавление полей в список отображаемых полей
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('telegram_username', 'phone', 'address', 'chat_id')}),
    )

# Регистрация кастомного пользователя в админ-панели
admin.site.register(CustomUser, CustomUserAdmin)

