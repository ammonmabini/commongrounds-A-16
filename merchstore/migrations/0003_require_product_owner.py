import django.db.models.deletion
from django.db import migrations, models


def assign_missing_product_owners(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    Product = apps.get_model('merchstore', 'Product')

    fallback_user, _ = User.objects.get_or_create(
        username='merchstore_owner',
        defaults={
            'email': 'merchstore-owner@example.com',
            'is_active': False,
        },
    )
    fallback_profile, _ = Profile.objects.get_or_create(
        user=fallback_user,
        defaults={
            'display_name': 'Merchstore Owner',
            'email_address': fallback_user.email,
            'role': 'Market Seller',
        },
    )

    Product.objects.filter(owner__isnull=True).update(owner=fallback_profile)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_create_missing_profiles'),
        ('merchstore', '0002_product_owner_product_product_image_product_status_and_more'),
    ]

    operations = [
        migrations.RunPython(
            assign_missing_product_owners,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='accounts.profile',
            ),
        ),
    ]
