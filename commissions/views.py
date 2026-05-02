from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.models import Profile

from .forms import CommissionForm, JobFormSet
from .models import Commission, Job
from .services import CommissionService


class CommissionMakerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        profile = getattr(self.request.user, "profile", None)
        return profile is not None and profile.role == "Commission Maker"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={self.request.path}")
        return HttpResponseForbidden("You do not have permission to access this page.")


class CommissionListView(ListView):
    model = Commission
    template_name = "commissions/commission_list.html"
    context_object_name = "all_commissions"

    def get_queryset(self):
        return (
            Commission.objects.select_related("maker", "maker__user", "type")
            .annotate(
                status_rank=Case(
                    When(status="Open", then=Value(0)),
                    When(status="Full", then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by("status_rank", "-created_on")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_commissions = list(context["all_commissions"])
        context["created_commissions"] = []
        context["applied_commissions"] = []

        if self.request.user.is_authenticated:
            profile = self.request.user.profile

            created_commissions = list(self.get_queryset().filter(maker=profile))
            applied_commissions = list(
                self.get_queryset().filter(job__jobapplication__applicant=profile).distinct()
            )

            excluded_ids = {commission.pk for commission in created_commissions + applied_commissions}

            context["created_commissions"] = created_commissions
            context["applied_commissions"] = applied_commissions
            context["all_commissions"] = [
                commission for commission in all_commissions if commission.pk not in excluded_ids
            ]

        return context


class CommissionDetailView(DetailView):
    model = Commission
    template_name = "commissions/commission_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.object
        jobs = commission.job_set.all().prefetch_related("jobapplication_set__applicant__user")

        current_profile = self.request.user.profile if self.request.user.is_authenticated else None
        job_rows = []

        for job in jobs:
            applications = list(
                job.jobapplication_set.all()
                .annotate(
                    status_rank=Case(
                        When(status="Pending", then=Value(0)),
                        When(status="Accepted", then=Value(1)),
                        When(status="Rejected", then=Value(2)),
                        default=Value(3),
                        output_field=IntegerField(),
                    )
                )
                .order_by("status_rank", "-applied_on")
            )

            accepted_count = sum(1 for application in applications if application.status == "Accepted")
            already_applied = False

            if current_profile is not None:
                already_applied = any(application.applicant_id == current_profile.pk for application in applications)

            job_rows.append(
                {
                    "job": job,
                    "accepted_count": accepted_count,
                    "already_applied": already_applied,
                    "applications": applications,
                }
            )

        context["jobs"] = job_rows
        context["summary"] = CommissionService.get_commission_summary(commission)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        job = get_object_or_404(Job, pk=request.POST.get("job_id"), commission=self.object)

        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        CommissionService.apply_to_job(request.user.profile, job)
        return redirect("commissions:commission-detail", pk=self.object.pk)


class CommissionCreateView(CommissionMakerRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = "commissions/commission_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_formset"] = JobFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context["job_formset"]

        if not job_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        jobs_data = []
        for subform in job_formset:
            if not subform.cleaned_data or subform.cleaned_data.get("DELETE"):
                continue

            role = subform.cleaned_data.get("role")
            manpower_required = subform.cleaned_data.get("manpower_required")
            status = subform.cleaned_data.get("status") or "Open"

            if role and manpower_required:
                jobs_data.append(
                    {
                        "role": role,
                        "manpower_required": manpower_required,
                        "status": status,
                    }
                )

        if not jobs_data:
            form.add_error(None, "Please add at least one job.")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = CommissionService.create_commission(
            author=self.request.user.profile,
            data=form.cleaned_data,
            jobs_data=jobs_data,
        )
        return redirect(self.object.get_absolute_url())


class CommissionUpdateView(CommissionMakerRequiredMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = "commissions/commission_form.html"

    def get_queryset(self):
        return Commission.objects.filter(maker=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_formset"] = JobFormSet(self.request.POST or None, instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context["job_formset"]

        if not job_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save(commit=False)
        self.object.maker = self.request.user.profile
        self.object.save()

        job_formset.instance = self.object
        job_formset.save()

        CommissionService.sync_commission_status(self.object)
        return redirect("commissions:commission-detail", pk=self.object.pk)