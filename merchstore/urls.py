from django.urls import path

from . import views

app_name = 'merchstore'

urlpatterns = [
    path('items', views.item_list, name='item_list'),
    path('item/<int:product_id>', views.item_detail, name='item_detail'),
]
