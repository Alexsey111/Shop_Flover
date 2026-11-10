from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from products.models import Cart, CartItem, Category, Order, OrderItem, Product, Review

User = get_user_model()


class ShopTestCase(TestCase):
    """Общая заготовка: категория, два товара и авторизованный покупатель."""

    def setUp(self):
        self.category = Category.objects.create(name="Розы")
        self.product = Product.objects.create(
            name="Роза красная",
            price=Decimal("150.00"),
            image="products/rose.jpg",
            category=self.category,
        )
        self.other = Product.objects.create(
            name="Тюльпан",
            price=Decimal("80.00"),
            image="products/tulip.jpg",
            category=self.category,
        )
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.client.force_login(self.user)

    def _cart(self):
        return Cart.objects.get(user=self.user)


class CatalogTests(ShopTestCase):
    def test_catalog_lists_products(self):
        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Роза красная")
        self.assertContains(response, "Тюльпан")

    def test_product_detail_shows_reviews_and_404_for_unknown_id(self):
        Review.objects.create(user=self.user, product=self.product, review="Свежие", rating=5)

        response = self.client.get(reverse("product_detail", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Свежие")

        missing = self.client.get(reverse("product_detail", args=[9999]))
        self.assertEqual(missing.status_code, 404)

    def test_anonymous_visitor_sees_catalog(self):
        self.client.logout()
        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)


class CartTests(ShopTestCase):
    def test_cart_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("view_cart"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_add_to_cart_increments_quantity_and_total(self):
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.client.get(reverse("add_to_cart", args=[self.other.id]))

        cart = self._cart()
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 2)
        self.assertEqual(cart.total_price, Decimal("380.00"))

    def test_remove_from_cart_decrements_then_deletes(self):
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        item = CartItem.objects.get(product=self.product)

        self.client.get(reverse("remove_from_cart", args=[item.id]))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)
        self.assertEqual(self._cart().total_price, Decimal("150.00"))

        self.client.get(reverse("remove_from_cart", args=[item.id]))
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())
        self.assertEqual(self._cart().total_price, Decimal("0.00"))

    def test_cart_page_shows_total(self):
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        response = self.client.get(reverse("view_cart"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "150")


class CheckoutTests(ShopTestCase):
    def _fill_cart(self):
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.client.get(reverse("add_to_cart", args=[self.other.id]))

    def test_checkout_creates_order_and_clears_cart(self):
        self._fill_cart()

        response = self.client.post(
            reverse("checkout"),
            {"delivery_option": "express", "payment_option": "cash_on_delivery"},
        )
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("order_preview", args=[order.id]))

        self.assertEqual(order.delivery_option, "express")
        self.assertEqual(order.payment_option, "cash_on_delivery")
        self.assertEqual(order.status, "pending")
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 2)
        self.assertEqual(order.total_price, Decimal("230.00"))
        self.assertEqual(CartItem.objects.filter(cart=self._cart()).count(), 0)

    def test_checkout_without_delivery_option_is_rejected(self):
        self._fill_cart()
        response = self.client.post(reverse("checkout"), {"payment_option": "paypal"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_confirm_order_completes_it_and_empties_cart(self):
        self._fill_cart()
        self.client.post(
            reverse("checkout"),
            {"delivery_option": "standard", "payment_option": "credit_card"},
        )
        order = Order.objects.get(user=self.user)

        response = self.client.post(reverse("confirm_order", args=[order.id]))
        self.assertRedirects(response, reverse("order_detail", args=[order.id]))

        order.refresh_from_db()
        self.assertEqual(order.status, "completed")
        self.assertEqual(CartItem.objects.filter(cart=self._cart()).count(), 0)

    def test_confirm_order_works_when_cart_is_missing(self):
        order = Order.objects.create(
            user=self.user, delivery_option="pickup", payment_option="credit_card"
        )
        Cart.objects.filter(user=self.user).delete()

        response = self.client.post(reverse("confirm_order", args=[order.id]))
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "completed")

    def test_confirm_order_saves_delivery_and_payment_from_preview(self):
        order = Order.objects.create(
            user=self.user, delivery_option="standard", payment_option="credit_card"
        )

        self.client.post(
            reverse("confirm_order", args=[order.id]),
            {"delivery_option": "pickup", "payment_option": "paypal"},
        )

        order.refresh_from_db()
        self.assertEqual(order.delivery_option, "pickup")
        self.assertEqual(order.payment_option, "paypal")
        self.assertEqual(order.status, "completed")

    def test_user_cannot_open_foreign_order(self):
        stranger = User.objects.create_user(username="stranger", password="pass12345")
        order = Order.objects.create(
            user=stranger, delivery_option="pickup", payment_option="credit_card"
        )
        response = self.client.get(reverse("order_detail", args=[order.id]))
        self.assertEqual(response.status_code, 404)


class ReviewTests(ShopTestCase):
    def test_add_review_saves_for_logged_user(self):
        response = self.client.post(
            reverse("add_review", args=[self.product.id]),
            {"review": "Доставили быстро", "rating": 5},
        )
        self.assertRedirects(response, reverse("product_detail", args=[self.product.id]))

        review = Review.objects.get(product=self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)

    def test_review_rating_outside_range_is_invalid(self):
        too_high = Review(user=self.user, product=self.product, review="Много", rating=6)
        with self.assertRaises(ValidationError):
            too_high.full_clean()

        too_low = Review(user=self.user, product=self.product, review="Мало", rating=0)
        with self.assertRaises(ValidationError):
            too_low.full_clean()

    def test_review_with_rating_above_five_is_not_saved_by_form(self):
        response = self.client.post(
            reverse("add_review", args=[self.product.id]),
            {"review": "Слишком много", "rating": 9},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())
