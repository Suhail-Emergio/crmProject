from django.db.models.signals import *
from django.dispatch import receiver
from crmAdmin.models import *
from datetime import datetime

def save_(status, lead, duty, report):
    if status == 'Follow Up' or status == 'Won':
        lead.lead_status = True
        lead.save()
        # report.follow =  report.follow + 1 if status == 'Follow Up' else report.follow
        if Target.objects.filter(sale=duty.emp, date=datetime.now(), type="Daily").exists():
            daily = Target.objects.get(sale=duty.emp, date=datetime.now(), type="Daily")
            daily.target_won += 1
            daily.target_remaining -= 1
            daily.save()
    elif status == 'Won':
        lead.closed = True
        lead.save()
    elif status == 'Lost':
        lead.assign_status = False
        lead.trash = True
        lead.save()
        if not TrashLead.objects.filter(lead=lead).exists():
            trash = TrashLead.objects.create(lead=lead,lost=True)
            trash.save()
        duty.delete()
    else:
        report.Notanswer += 1
    # report.save()

# Update when a lead status is created
@receiver(post_save, sender=Leadstatus)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        lead = instance.lead
        duty = Duty.objects.get(lead=lead)
        report = SaleReport.objects.filter(date=datetime.now(), emp=duty.emp)

        if Callback.objects.filter(duty=duty).exists():
            Callback.objects.filter(duty=duty).delete()

        save_(instance.status, lead, duty, report)

        lead_statuses = Leadstatus.objects.filter(lead=lead)[:3]
        all_false = len(lead_statuses) > 0 and all(status.status == "Not Answering" for status in lead_statuses)
        if all_false:
            lead.assign_status = False
            lead.trash =True
            lead.save()
            if not TrashLead.objects.filter(lead=lead).exists():
                trash = TrashLead.objects.create(lead=lead,lost=False)
                trash.save()
            duty.delete()


@receiver(post_save, sender=Won)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        duty = Duty.objects.get(lead=instance.lead)
        admin = Admins.objects.get(id=duty.emp.admin.id)
        admin.target_won += instance.course.rate
        admin.save()
        duty.delete()
        lead = instance.lead
        lead.closed = True
        lead.save()
        daily = Target.objects.get(sale=instance.employee, date__month=datetime.now().month, type="Monthly")
        daily.target_won += instance.course.rate
        daily.target_remaining -= instance.course.rate
        daily.save()