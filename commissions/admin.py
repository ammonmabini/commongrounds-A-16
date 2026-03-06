from django.contrib import admin

from .models import Commission, CommissionType


@admin.register(CommissionType)
class CommissionTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("title", "people_required", "created_on", "updated_on")
    search_fields = ("title",)
    list_filter = ("created_on",)
    ordering = ("created_on",)