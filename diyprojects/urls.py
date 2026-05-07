from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)

app_name = 'diyprojects'

urlpatterns = [
    path(
        'projects',
        ProjectListView.as_view(),
        name='project-list',
    ),

    path(
        'project/add',
        ProjectCreateView.as_view(),
        name='project-add',
    ),

    path(
        'project/<int:pk>',
        ProjectDetailView.as_view(),
        name='project-detail',
    ),

    path(
        'project/<int:pk>/edit',
        ProjectUpdateView.as_view(),
        name='project-edit',
    ),
]