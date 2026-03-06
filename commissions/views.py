from django.views.generic import DetailView, ListView

from .models import Commission


class CommissionListView(ListView):
    model = Commission
    template_name = "commissions/commission_list.html"
    context_object_name = "commissions"


class CommissionDetailView(DetailView):
    model = Commission
    template_name = "commissions/commission_detail.html"
    context_object_name = "commission"
