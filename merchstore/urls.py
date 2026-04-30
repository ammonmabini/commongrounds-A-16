from django.urls import path

from . import views

app_name = 'merchstore'

urlpatterns = [
    path('items', views.item_list, name='item_list'),
    path(
        'item/<int:product_id>',
        views.ProductDetailView.as_view(),
        name='item_detail',
    ),
    path('item/add', views.ProductCreateView.as_view(), name='item_create'),
    path(
        'item/<int:product_id>/edit',
        views.ProductUpdateView.as_view(),
        name='item_update',
    ),
    path('cart', views.cart, name='cart'),
    path('transactions', views.transactions_list, name='transactions'),
    path(
        'complete-pending-purchase',
        views.complete_pending_purchase,
        name='complete_pending_purchase',
    ),
]
