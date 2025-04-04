from django.db.models.signals import *
from django.dispatch import receiver
from .models import *
from datetime import datetime

# Update sale report when Duty is created
# @receiver(post_save, sender=Duty)
# def save_handler(sender, created, instance, **kwargs):
#     if created:
#         report = SaleReport.objects.get(date=datetime.now(), emp=instance.emp)
#         report.total += 1
#         report.save()

# Update Employers Details when Employee (Model) is deleted
@receiver(pre_delete, sender=Employee)
def before_delete_handler(sender, instance, **kwargs):
    if Duty.objects.filter(emp=instance).exists():
        Duty.objects.filter(emp=instance).delete()

# Update Employers Details and Lead Details when Duty (Model) is deleted
@receiver(pre_delete, sender=Duty)
def before_delete_handler(sender, instance, **kwargs):
    emp = instance.emp
    if instance.created_on == datetime.now().date():
        emp.todays_lead -= 1
    emp.total_lead -= 1
    if emp.todays_lead > emp.total_lead:
        emp.total_lead = emp.todays_lead
    emp.save()
    leads = instance.lead
    leads.assign_status = False
    leads.save()