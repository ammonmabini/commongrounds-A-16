from django.shortcuts import get_object_or_404

from .models import Project


class ProjectRepository:
    def get_all(self):
        return Project.objects.all()

    def get_by_category(self, category_name):
        return Project.objects.filter(
            category__name=category_name
        )

    def get_recent(self, n):
        return Project.objects.order_by(
            '-created_on'
        )[:n]

    def get_by_id(self, id):
        return get_object_or_404(
            Project,
            pk=id,
        )