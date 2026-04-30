from django.shortcuts import redirect
from django.urls import reverse

from .models import Transaction


class BaseTransactionStrategy:
    def execute(self, request, product, form):
        raise NotImplementedError('Subclasses must implement execute().')


class AuthenticatedPurchaseStrategy(BaseTransactionStrategy):
    def execute(self, request, product, form):
        transaction = form.save(commit=False)
        transaction.buyer = request.user.profile
        transaction.product = product
        transaction.status = Transaction.STATUS_ON_CART
        transaction.save()
        return redirect('merchstore:cart')


class GuestPurchaseStrategy(BaseTransactionStrategy):
    def execute(self, request, product, form):
        request.session['pending_purchase'] = {
            'product_id': product.pk,
            'amount': form.cleaned_data.get('amount'),
        }
        request.session.modified = True
        login_url = reverse('login')
        next_url = reverse('merchstore:complete_pending_purchase')
        return redirect(f'{login_url}?next={next_url}')
