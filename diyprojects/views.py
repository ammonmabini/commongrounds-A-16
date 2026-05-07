from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.core.exceptions import PermissionDenied

from .forms import (
    ProjectForm,
    ProjectRatingForm,
    ProjectReviewForm,
)
from .models import Favorite, Project
from .repositories import ProjectRepository


class ProjectListView(View):
    template_name = 'diyprojects/project_list.html'
    repository = ProjectRepository()

    def get(self, request):
        projects = self.repository.get_all()

        context = {
            'projects': projects,
        }

        if request.user.is_authenticated:
            profile = request.user.profile

            created_projects = projects.filter(
                creator=profile
            )

            favorited_projects = projects.filter(
                favorites__profile=profile
            )

            reviewed_projects = projects.filter(
                reviews__reviewer=profile
            )

            grouped_ids = list(
                created_projects.values_list(
                    'id',
                    flat=True,
                )
            )

            grouped_ids += list(
                favorited_projects.values_list(
                    'id',
                    flat=True,
                )
            )

            grouped_ids += list(
                reviewed_projects.values_list(
                    'id',
                    flat=True,
                )
            )

            context = {
                'created_projects': created_projects,
                'favorited_projects': favorited_projects,
                'reviewed_projects': reviewed_projects,
                'projects': projects.exclude(
                    id__in=grouped_ids
                ),
            }

        return render(
            request,
            self.template_name,
            context,
        )


class ProjectDetailView(View):
    template_name = 'diyprojects/project_detail.html'
    repository = ProjectRepository()

    def get(self, request, pk):
        project = self.repository.get_by_id(pk)

        ratings = project.ratings.all()

        if ratings.count() > 0:
            average_rating = (
                sum(r.score for r in ratings)
                / ratings.count()
            )
        else:
            average_rating = None

        context = {
            'project': project,
            'favorite_count': project.favorites.count(),
            'average_rating': average_rating,
            'reviews': project.reviews.all(),
            'rating_form': ProjectRatingForm(),
            'review_form': ProjectReviewForm(),
        }

        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('login')

        project = self.repository.get_by_id(pk)
        profile = request.user.profile

        if 'favorite' in request.POST:
            Favorite.objects.get_or_create(
                project=project,
                profile=profile,
            )

        elif 'rating' in request.POST:
            form = ProjectRatingForm(request.POST)

            if form.is_valid():
                rating = form.save(commit=False)
                rating.project = project
                rating.profile = profile
                rating.save()

        elif 'review' in request.POST:
            form = ProjectReviewForm(
                request.POST,
                request.FILES,
            )

            if form.is_valid():
                review = form.save(commit=False)
                review.project = project
                review.reviewer = profile
                review.save()

        return redirect(
            project.get_absolute_url()
        )

class ProjectCreatorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied

        if (
            request.user.profile.role
            != 'Project Creator'
        ):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

class ProjectCreateView(
    LoginRequiredMixin,
    ProjectCreatorRequiredMixin,
    CreateView,
):
    model = Project
    form_class = ProjectForm
    template_name = 'diyprojects/project_form.html'

    def form_valid(self, form):
        form.instance.creator = (
            self.request.user.profile
        )

        return super().form_valid(form)


class ProjectUpdateView(
    LoginRequiredMixin,
    ProjectCreatorRequiredMixin,
    UpdateView,
):
    model = Project
    form_class = ProjectForm
    template_name = 'diyprojects/project_form.html'