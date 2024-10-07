from django import forms
from .models import Category, Order, Review
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Выберите категорию"
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Минимальная цена'})
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Максимальная цена'})
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Поиск по названию'})
    )

class CheckoutForm(forms.ModelForm):
    delivery_option = forms.ChoiceField(
        choices=Order.DELIVERY_CHOICES,
        required=True,
        label="Выберите способ доставки"
    )
    payment_option = forms.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        required=True,
        label="Выберите способ оплаты"
    )

    class Meta:
        model = Order
        fields = ['delivery_option', 'payment_option']

class OrderPreviewForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_option', 'payment_option']



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_option', 'payment_option']  # Убедитесь, что указаны только существующие поля
        widgets = {
            'delivery_option': forms.Select(choices=Order.DELIVERY_CHOICES),
            'payment_option': forms.Select(choices=Order.PAYMENT_CHOICES),
        }


class ConfirmLogoutForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Ваш пароль')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'review': 'Отзыв',
            'rating': 'Оценка',
        }

