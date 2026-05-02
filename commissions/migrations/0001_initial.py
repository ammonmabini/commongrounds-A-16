from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommissionType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Commission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("people_required", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("Open", "Open"), ("Full", "Full")], default="Open", max_length=10)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "maker",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="accounts.profile"),
                ),
                (
                    "type",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="commissions.commissiontype"),
                ),
            ],
            options={
                "ordering": ["created_on"],
            },
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(max_length=255)),
                ("manpower_required", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("Open", "Open"), ("Full", "Full")], default="Open", max_length=10)),
                (
                    "commission",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="commissions.commission"),
                ),
            ],
            options={
                "ordering": ["-status", "-manpower_required", "role"],
            },
        ),
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")], default="Pending", max_length=10)),
                ("applied_on", models.DateTimeField(auto_now_add=True)),
                (
                    "applicant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="accounts.profile"),
                ),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="commissions.job"),
                ),
            ],
            options={
                "ordering": ["status", "-applied_on"],
            },
        ),
    ]