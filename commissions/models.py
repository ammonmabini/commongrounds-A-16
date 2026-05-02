from django.db import models
from django.db.models import Case, IntegerField, Value, When
from django.urls import reverse

from accounts.models import Profile


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Commission(models.Model):
    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Full", "Full"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.ForeignKey(CommissionType, on_delete=models.SET_NULL, null=True, blank=True)
    maker = models.ForeignKey(Profile, on_delete=models.CASCADE)
    people_required = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Open")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("commissions:commission-detail", kwargs={"pk": self.pk})


class Job(models.Model):
    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Full", "Full"),
    ]

    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    manpower_required = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Open")

    class Meta:
        ordering = ["-status", "-manpower_required", "role"]

    def __str__(self):
        return f"{self.role} ({self.commission.title})"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            Case(
                When(status="Pending", then=Value(0)),
                When(status="Accepted", then=Value(1)),
                When(status="Rejected", then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            ),
            "-applied_on",
    ]

    def __str__(self):
        applicant_name = self.applicant.display_name or self.applicant.user.username
        return f"{applicant_name} - {self.job.role}"