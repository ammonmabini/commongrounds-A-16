from django.contrib import admin

from .models import Project, ProjectCategory


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_on')
    list_filter = ('category',)
    search_fields = ('title',)
