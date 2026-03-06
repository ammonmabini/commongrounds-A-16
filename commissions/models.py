from django.db import models


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["name"]  # sort by name ASC

    def __str__(self) -> str:
        return self.name


class Commission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    people_required = models.PositiveIntegerField()  # whole number (>= 0)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_on"]  # sort by created_on ASC

    def __str__(self) -> str:
        return f"{self.title} (needs {self.people_required})"