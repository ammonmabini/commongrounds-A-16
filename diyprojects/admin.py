from django.contrib import admin

from .models import (
    Favorite,
    Project,
    ProjectCategory,
    ProjectRating,
    ProjectReview,
)


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0


class ProjectReviewInline(admin.TabularInline):
    model = ProjectReview
    extra = 0


class ProjectRatingInline(admin.TabularInline):
    model = ProjectRating
    extra = 0


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'creator',
        'created_on',
    )

    list_filter = (
        'category',
        'created_on',
    )

    search_fields = (
        'title',
        'description',
    )

    inlines = [
        FavoriteInline,
        ProjectReviewInline,
        ProjectRatingInline,
    ]


admin.site.register(Favorite)
admin.site.register(ProjectReview)
admin.site.register(ProjectRating)