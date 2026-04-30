from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, Transaction


@receiver(post_save, sender=Transaction)
def deduct_product_stock(sender, instance, created, **kwargs):
    if not created:
        return

    product = instance.product
    Product.objects.filter(
        pk=product.pk,
        stock__gte=instance.amount,
    ).update(
        stock=F('stock') - instance.amount,
    )
    product.refresh_from_db()
    product.update_stock_status()
    product.save(update_fields=['status'])
