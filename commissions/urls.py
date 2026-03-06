from django.urls import path

from .views import CommissionDetailView, CommissionListView

app_name = "commissions"

urlpatterns = [
    # /commissions/requests
    path("requests", CommissionListView.as_view(), name="request_list"),
    # /commissions/request/1
    path("request/<int:pk>", CommissionDetailView.as_view(), name="request_detail"),
]