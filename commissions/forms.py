from django import forms
from django.forms import inlineformset_factory

from .models import Commission, Job, JobApplication


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        exclude = ["maker"]
        widgets = {
            "status": forms.Select(),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["job"]
        widgets = {
            "job": forms.HiddenInput(),
        }


JobFormSet = inlineformset_factory(
    Commission,
    Job,
    fields=["role", "manpower_required", "status"],
    extra=1,
    can_delete=True,
)