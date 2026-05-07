from django import forms

from .models import (
    Project,
    ProjectRating,
    ProjectReview,
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'category',
            'description',
            'materials',
            'steps',
        ]


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectReview
        fields = [
            'comment',
            'image',
        ]


class ProjectRatingForm(forms.ModelForm):
    class Meta:
        model = ProjectRating
        fields = [
            'score',
        ]

    def clean_score(self):
        score = self.cleaned_data['score']

        if score < 1 or score > 10:
            raise forms.ValidationError(
                'Score must be between 1 and 10.'
            )

        return score