from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from accounts.models import Profile


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_AVAILABLE = 'Available'
    STATUS_ON_SALE = 'On sale'
    STATUS_OUT_OF_STOCK = 'Out of stock'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ON_SALE, 'On sale'),
        (STATUS_OUT_OF_STOCK, 'Out of stock'),
    ]

    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(
        ProductType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
    )
    owner = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='products',
    )
    product_image = models.ImageField(
        upload_to='merchstore/products/',
        null=True,
        blank=True,
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('merchstore:item_detail', kwargs={'product_id': self.pk})

    def update_stock_status(self):
        if self.stock == 0:
            self.status = self.STATUS_OUT_OF_STOCK
        elif self.status == self.STATUS_OUT_OF_STOCK:
            self.status = self.STATUS_AVAILABLE

    def save(self, *args, **kwargs):
        self.update_stock_status()
        super().save(*args, **kwargs)


class Transaction(models.Model):
    STATUS_ON_CART = 'On cart'
    STATUS_TO_PAY = 'To Pay'
    STATUS_TO_SHIP = 'To Ship'
    STATUS_TO_RECEIVE = 'To Receive'
    STATUS_DELIVERED = 'Delivered'

    STATUS_CHOICES = [
        (STATUS_ON_CART, 'On cart'),
        (STATUS_TO_PAY, 'To Pay'),
        (STATUS_TO_SHIP, 'To Ship'),
        (STATUS_TO_RECEIVE, 'To Receive'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    buyer = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchases',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ON_CART,
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return '{} x{} for {}'.format(
            self.product.name,
            self.amount,
            self.buyer or 'Guest',
        )

    def clean(self):
        if (
            self.product_id
            and self.amount
            and self.pk is None
            and self.amount > self.product.stock
        ):
            raise ValidationError({
                'amount': 'There is not enough stock available.',
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
