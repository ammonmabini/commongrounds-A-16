from django import forms

from .models import Product, Transaction


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'name',
            'product_type',
            'product_image',
            'description',
            'price',
            'stock',
            'status',
        )


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('amount',)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.product and amount and amount > self.product.stock:
            raise forms.ValidationError('There is not enough stock available.')
        return amount
