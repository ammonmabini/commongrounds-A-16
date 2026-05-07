from django.db import models
from django.urls import reverse
from accounts.models import Profile


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL,
        null=True,
        related_name='projects',
    )
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects',
    )

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
            return self.title

    def get_absolute_url(self):
        return reverse('diyprojects:project-detail', args=[self.pk])


class Favorite(models.Model):
    BACKLOG = 'Backlog'
    TODO = 'To-Do'
    DONE = 'Done'

    STATUS_CHOICES = [
        (BACKLOG, 'Backlog'),
        (TODO, 'To-Do'),
        (DONE, 'Done'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='favorite_projects',
    )
    date_favorited = models.DateField(auto_now_add=True)
    project_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=BACKLOG,
    )

    def __str__(self):
        return f'{self.profile} favorited {self.project}'


class ProjectReview(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_reviews',
    )
    comment = models.TextField()
    image = models.ImageField(
        upload_to='project_reviews/',
        blank=True,
    )

    def __str__(self):
        return f'Review for {self.project}'


class ProjectRating(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_ratings',
    )
    score = models.IntegerField()

    def __str__(self):
        return f'{self.project}: {self.score}/10'