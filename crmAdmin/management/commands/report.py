from django.core.management.base import BaseCommand
from crmAdmin.models import *
from django.utils import timezone
from datetime import timedelta, datetime
from crmAdmin.utils.report_util import *
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Update Daily'
    def handle(self, *args, **kwargs):
        self.followup()

        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1) if start_of_month.month == 12 else start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)

        if today == end_of_month:
            self.monthly_follow(start_of_month, end_of_month)
            self.monthly_won(start_of_month, end_of_month)
            self.delete_follow()

    def followup(self):
        today = timezone.now().date()
        for j in Admins.objects.all():
            duty = Duty.objects.filter(lead__lead_status=True, lead__closed=False, lead__admin=j.user).order_by('-id')
            print(Duty.objects.filter(lead__admin=j.user),j.user)
            array = []
            for i in duty:
                print("working")
                if Leadstatus.objects.filter(lead=i.lead,contacted_on=today).exists():
                    for leads in Leadstatus.objects.filter(lead=i.lead,contacted_on=today):
                        saleperson = i.emp.user.name if i.emp else "-"
                        array.append((saleperson, leads))
                        print(array)
            header = f'{j}_followups ' +today.strftime('%Y-%m-%d')+'.csv'
            header_row = [ '#', 'sale', 'lead', 'lead_number','progress', 'course', 'course_value', 'notes' ]
            create_report(array, header, header_row, "followup", j.user)

    def monthly_won(self, start_of_month, end_of_month):
        today = timezone.now().date()
        for j in Admins.objects.all():
            array = Won.objects.filter(won_on__gte=start_of_month,won_on__lte=end_of_month, lead__admin=j.user).order_by('-won_on')
            header_row = [ '#', 'sale', 'lead', 'lead_number', 'course', 'course_value', 'mode' ]
            header = 'monthly_won'+today.strftime('%m')+'.csv'
            create_report(array, header, header_row, "monthly_won", j.user)

    def monthly_follow(self, start_of_month, end_of_month):
        today = timezone.now().date()
        for j in Admins.objects.all():
            duties = Duty.objects.filter(lead__lead_status=True, lead__closed=False, lead__trash=False, lead__admin=j.user).order_by('-id')
            array = []
            for i in duties:
                if Leadstatus.objects.filter(lead=i.lead,contacted_on__gte=start_of_month,contacted_on__lte=end_of_month).exists():
                    for leads in Leadstatus.objects.filter(lead=i.lead,contacted_on=today):
                        saleperson = i.emp.user.name if i.emp else "-"
                        array.append((saleperson, leads))
            header = 'monthly_followups ' +today.strftime('%Y-%m-%d')+'.csv'
            header_row = [ '#', 'sale', 'lead', 'lead_number','progress', 'course', 'course_value', 'notes' ]
            create_report(array, header, header_row, "monthly_followup", j.user)

    def delete_follow(self):
        for i in Report.objects.filter(name= 'followup'):
            if i.csv:
                file_path = os.path.join(settings.MEDIA_ROOT, i.csv.name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                i.csv.delete(save = False)
            i.delete()