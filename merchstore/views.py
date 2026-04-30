from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.edit import CreateView, UpdateView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .forms import ProductForm, TransactionForm
from .models import Product, Transaction
from .strategies import (
    AuthenticatedPurchaseStrategy,
    GuestPurchaseStrategy,
)


def item_list(request):
    all_products = Product.objects.select_related(
        'product_type',
        'owner',
        'owner__user',
    )
    user_products = Product.objects.none()

    if request.user.is_authenticated:
        user_products = all_products.filter(owner=request.user.profile)
        all_products = all_products.exclude(owner=request.user.profile)

    return render(request, 'merchstore/item_list.html', {
        'user_products': user_products,
        'items': all_products,
    })


class ProductDetailView(View):
    template_name = 'merchstore/item_detail.html'

    def get_product(self, product_id):
        return get_object_or_404(
            Product.objects.select_related('product_type', 'owner', 'owner__user'),
            pk=product_id,
        )

    def get_context_data(self, product, form=None):
        return {
            'item': product,
            'form': form or TransactionForm(product=product),
        }

    def get(self, request, product_id):
        product = self.get_product(product_id)
        return render(
            request,
            self.template_name,
            self.get_context_data(product),
        )

    def post(self, request, product_id):
        product = self.get_product(product_id)
        form = TransactionForm(request.POST, product=product)

        if request.user.is_authenticated and product.owner == request.user.profile:
            messages.error(request, 'You cannot purchase your own product.')
            return render(
                request,
                self.template_name,
                self.get_context_data(product, form),
            )

        if form.is_valid():
            strategy = (
                AuthenticatedPurchaseStrategy()
                if request.user.is_authenticated
                else GuestPurchaseStrategy()
            )
            return strategy.execute(request, product, form)

        return render(
            request,
            self.template_name,
            self.get_context_data(product, form),
        )


class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchstore/product_form.html'
    required_role = Profile.ROLE_MARKET_SELLER

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchstore/product_form.html'
    pk_url_kwarg = 'product_id'
    required_role = Profile.ROLE_MARKET_SELLER

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user.profile)

    def form_valid(self, form):
        if form.instance.stock == 0:
            form.instance.status = Product.STATUS_OUT_OF_STOCK
        else:
            form.instance.status = Product.STATUS_AVAILABLE
        return super().form_valid(form)


@login_required
def cart(request):
    transactions = Transaction.objects.select_related(
        'product',
        'product__owner',
        'buyer',
    ).filter(buyer=request.user.profile)
    grouped_transactions = defaultdict(list)

    for transaction in transactions:
        grouped_transactions[transaction.product.owner].append(transaction)

    return render(request, 'merchstore/cart.html', {
        'grouped_transactions': dict(grouped_transactions),
    })


@login_required
@role_required(Profile.ROLE_MARKET_SELLER)
def transactions_list(request):
    transactions = Transaction.objects.select_related(
        'product',
        'product__owner',
        'buyer',
    ).filter(product__owner=request.user.profile)
    grouped_transactions = defaultdict(list)

    for transaction in transactions:
        grouped_transactions[transaction.buyer].append(transaction)

    return render(request, 'merchstore/transactions.html', {
        'grouped_transactions': dict(grouped_transactions),
    })


@login_required
def complete_pending_purchase(request):
    pending_purchase = request.session.get('pending_purchase')
    if not pending_purchase:
        return redirect('merchstore:cart')

    product = get_object_or_404(Product, pk=pending_purchase.get('product_id'))
    form = TransactionForm(pending_purchase, product=product)
    if not form.is_valid():
        request.session.pop('pending_purchase', None)
        messages.error(request, 'The pending purchase could not be completed.')
        return redirect(product.get_absolute_url())

    request.session.pop('pending_purchase', None)
    return AuthenticatedPurchaseStrategy().execute(request, product, form)
