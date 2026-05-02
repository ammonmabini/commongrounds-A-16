from django.db import transaction

from .models import Commission, Job, JobApplication


class CommissionService:
    @staticmethod
    @transaction.atomic
    def create_commission(author, data, jobs_data):
        commission = Commission.objects.create(maker=author, **data)

        for job_data in jobs_data:
            role = (job_data.get("role") or "").strip()
            manpower_required = job_data.get("manpower_required")
            status = job_data.get("status") or "Open"

            if role and manpower_required:
                Job.objects.create(
                    commission=commission,
                    role=role,
                    manpower_required=manpower_required,
                    status=status,
                )

        CommissionService.sync_commission_status(commission)
        return commission

    @staticmethod
    def apply_to_job(applicant, job):
        if job.commission.maker == applicant:
            return None

        if JobApplication.objects.filter(applicant=applicant, job=job).exists():
            return None

        accepted_count = job.jobapplication_set.filter(status="Accepted").count()

        if job.status == "Full" or accepted_count >= job.manpower_required:
            job.status = "Full"
            job.save()
            CommissionService.sync_commission_status(job.commission)
            return None

        application = JobApplication.objects.create(
            job=job,
            applicant=applicant,
            status="Pending",
        )

        CommissionService.sync_commission_status(job.commission)
        return application
    
    @staticmethod
    def sync_commission_status(commission):
        jobs = commission.job_set.all()

        if not jobs.exists():
            commission.status = "Open"
            commission.save()
            return commission

        all_full = True
        for job in jobs:
            accepted_count = job.jobapplication_set.filter(status="Accepted").count()
            if accepted_count >= job.manpower_required:
                if job.status != "Full":
                    job.status = "Full"
                    job.save()
            else:
                all_full = False
                if job.status != "Open":
                    job.status = "Open"
                    job.save()

        commission.status = "Full" if all_full else "Open"
        commission.save()
        return commission

    @staticmethod
    def get_commission_summary(commission):
        total_manpower = 0
        open_manpower = 0

        for job in commission.job_set.all():
            accepted_count = job.jobapplication_set.filter(status="Accepted").count()
            total_manpower += job.manpower_required
            remaining = job.manpower_required - accepted_count
            if remaining > 0:
                open_manpower += remaining

        return {
            "total_manpower": total_manpower,
            "open_manpower": open_manpower,
        }