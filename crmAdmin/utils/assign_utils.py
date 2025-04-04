#################################  A S S I G N  L E A D S  #################################
from crmAdmin.models import *
from django.utils import timezone
from datetime import timedelta, datetime

def assign_leads(lead):
    emp = Employee.objects.filter(admin=lead.admin)
    for i in emp:
        if i.todays_lead !=  i.strength and not lead.assign_status and i.strength > 0:
            thirty_days = timezone.now().date() + timedelta(days=1)
            duty = Duty.objects.create(lead=lead,emp=i,delete_date=thirty_days)
            duty.save()
            i.todays_lead += 1
            i.total_lead += 1
            i.save()
            lead.assign_status = True
            lead.save()