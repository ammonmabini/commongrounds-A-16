from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile

from .models import Product, ProductType, Transaction


class MerchandiseStoreTests(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(
            username='seller',
            password='StrongPassword123',
        )
        self.seller_user.profile.display_name = 'Seller'
        self.seller_user.profile.role = Profile.ROLE_MARKET_SELLER
        self.seller_user.profile.save()

        self.buyer_user = User.objects.create_user(
            username='buyer',
            password='StrongPassword123',
        )
        self.buyer_user.profile.display_name = 'Buyer'
        self.buyer_user.profile.save()

        self.product_type = ProductType.objects.create(
            name='Shirt',
            description='Wearable merchandise',
        )
        self.product = Product.objects.create(
            name='Common Grounds Shirt',
            product_type=self.product_type,
            owner=self.seller_user.profile,
            description='Cotton shirt',
            price=Decimal('500.00'),
            stock=5,
        )

    def test_market_seller_can_create_product(self):
        self.client.force_login(self.seller_user)

        response = self.client.post(reverse('merchstore:item_create'), {
            'name': 'Sticker Pack',
            'product_type': self.product_type.pk,
            'description': 'Five stickers',
            'price': '99.00',
            'stock': '10',
            'status': Product.STATUS_AVAILABLE,
        })

        product = Product.objects.get(name='Sticker Pack')
        self.assertRedirects(response, product.get_absolute_url())
        self.assertEqual(product.owner, self.seller_user.profile)

    def test_product_owner_is_required(self):
        owner_field = Product._meta.get_field('owner')

        self.assertFalse(owner_field.null)

    def test_non_seller_cannot_create_product(self):
        self.client.force_login(self.buyer_user)

        response = self.client.get(reverse('merchstore:item_create'))

        self.assertRedirects(
            response,
            reverse('accounts:permission_denied'),
            fetch_redirect_response=False,
        )

    def test_product_update_sets_status_from_stock(self):
        self.client.force_login(self.seller_user)
        self.product.status = Product.STATUS_ON_SALE
        self.product.save()

        response = self.client.post(
            reverse('merchstore:item_update', kwargs={'product_id': self.product.pk}),
            {
                'name': self.product.name,
                'product_type': self.product_type.pk,
                'description': self.product.description,
                'price': self.product.price,
                'stock': '3',
                'status': Product.STATUS_ON_SALE,
            },
        )

        self.assertRedirects(response, self.product.get_absolute_url())
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, Product.STATUS_AVAILABLE)

        response = self.client.post(
            reverse('merchstore:item_update', kwargs={'product_id': self.product.pk}),
            {
                'name': self.product.name,
                'product_type': self.product_type.pk,
                'description': self.product.description,
                'price': self.product.price,
                'stock': '0',
                'status': Product.STATUS_AVAILABLE,
            },
        )

        self.assertRedirects(response, self.product.get_absolute_url())
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, Product.STATUS_OUT_OF_STOCK)

    def test_transaction_creation_deducts_product_stock(self):
        Transaction.objects.create(
            buyer=self.buyer_user.profile,
            product=self.product,
            amount=2,
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.product.status, Product.STATUS_AVAILABLE)

    def test_transaction_marks_product_out_of_stock(self):
        Transaction.objects.create(
            buyer=self.buyer_user.profile,
            product=self.product,
            amount=5,
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertEqual(self.product.status, Product.STATUS_OUT_OF_STOCK)

    def test_transaction_cannot_exceed_available_stock(self):
        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                buyer=self.buyer_user.profile,
                product=self.product,
                amount=6,
            )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_product_detail_purchase_redirects_to_cart(self):
        self.client.force_login(self.buyer_user)

        response = self.client.post(
            reverse('merchstore:item_detail', kwargs={'product_id': self.product.pk}),
            {'amount': 1},
        )

        self.assertRedirects(response, reverse('merchstore:cart'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)
        self.assertTrue(Transaction.objects.filter(
            buyer=self.buyer_user.profile,
            product=self.product,
            amount=1,
        ).exists())
