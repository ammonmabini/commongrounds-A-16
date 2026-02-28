from django.shortcuts import get_object_or_404, render

from .models import Product


def item_list(request):
    items = Product.objects.select_related('product_type').all()
    return render(request, 'merchstore/item_list.html', {'items': items})


def item_detail(request, product_id):
    item = get_object_or_404(
        Product.objects.select_related('product_type'),
        pk=product_id,
    )
    return render(request, 'merchstore/item_detail.html', {'item': item})
