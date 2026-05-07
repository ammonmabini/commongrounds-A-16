from django.conf import settings
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    ROLE_MEMBER = 'Member'
    ROLE_MARKET_SELLER = 'Market Seller'
    ROLE_EVENT_ORGANIZER = 'Event Organizer'
    ROLE_BOOK_CONTRIBUTOR = 'Book Contributor'
    ROLE_COMMISSION_MAKER = 'Commission Maker'
    ROLE_PROJECT_CREATOR = 'Project Creator'

    ROLE_CHOICES = [
        (ROLE_MEMBER, 'Member'),
        (ROLE_MARKET_SELLER, 'Market Seller'),
        (ROLE_EVENT_ORGANIZER, 'Event Organizer'),
        (ROLE_BOOK_CONTRIBUTOR, 'Book Contributor'),
        (ROLE_COMMISSION_MAKER, 'Commission Maker'),
        (ROLE_PROJECT_CREATOR, 'Project Creator'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(max_length=63)
    email_address = models.EmailField()
    role = models.CharField(
        max_length=31,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name or self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile_update', kwargs={
            'username': self.user.username,
        })
