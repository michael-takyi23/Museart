import pytest
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from checkout.models import Order, Product
from django.template.loader import render_to_string
from bs4 import BeautifulSoup


@pytest.mark.django_db
class TestStripePayment(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Create a sample product for the cart
        self.product = Product.objects.create(
            name='Test Product',
            price=20.00,
            description='A test product.'
        )

        # Add the product to the cart in the session
        self.cart = {
            str(self.product.id): {
                'product': self.product,
                'quantity': 1,
                'subtotal': self.product.price,
            }
        }
        self.client.session['cart'] = self.cart  # Add the cart to the session
        self.client.session.save()

    def test_checkout_view_payment_success(self):
        # Simulate a successful payment with Stripe test card
        stripe_token = 'tok_visa'  # Stripe test token for successful payment

        # Make sure the checkout view is accessible
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200, f"Failed to load checkout page. Redirected to {response['Location']}")

        # Generate the CSRF token for the form
        csrf_token = response.cookies['csrftoken'].value

        # Simulate filling in the form
        response = self.client.post(reverse('checkout'), {
            'stripeToken': stripe_token,
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'postcode': '12345',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'street_address2': '',
            'save_info': 'on',  # Only if user is authenticated and has the checkbox
            'csrfmiddlewaretoken': csrf_token  # Include CSRF token
        })

        # Ensure that the order is created
        self.assertEqual(response.status_code, 302)  # Redirection to order confirmation
        order = Order.objects.first()
        self.assertEqual(order.status, 'Paid')
        self.assertEqual(order.user, self.user)

    def test_checkout_view_payment_declined(self):
        # Simulate a declined payment with Stripe test card
        stripe_token = 'tok_chargeDeclined'  # Stripe test token for declined payment

        # Make sure the checkout view is accessible
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200, f"Failed to load checkout page. Redirected to {response['Location']}")

        # Generate the CSRF token for the form
        csrf_token = response.cookies['csrftoken'].value

        # Simulate filling in the form with a declined payment
        response = self.client.post(reverse('checkout'), {
            'stripeToken': stripe_token,
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'postcode': '12345',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'street_address2': '',
            'save_info': 'on',  # Only if user is authenticated and has the checkbox
            'csrfmiddlewaretoken': csrf_token  # Include CSRF token
        })

        # Ensure that the error message is displayed for declined payment
        self.assertContains(response, "Your card was declined. Please try again.")
