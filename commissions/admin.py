from django.contrib import admin

from .models import Commission, CommissionType, Job, JobApplication


@admin.register(CommissionType)
class CommissionTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class JobInline(admin.TabularInline):
    model = Job
    extra = 1


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("title", "maker", "people_required", "status", "created_on", "updated_on")
    search_fields = ("title", "maker__display_name", "maker__user__username")
    list_filter = ("status", "type", "created_on")
    ordering = ("created_on",)
    inlines = [JobInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("role", "commission", "manpower_required", "status")
    search_fields = ("role", "commission__title")
    list_filter = ("status",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "applied_on")
    search_fields = ("job__role", "job__commission__title", "applicant__display_name", "applicant__user__username")
    list_filter = ("status", "applied_on")