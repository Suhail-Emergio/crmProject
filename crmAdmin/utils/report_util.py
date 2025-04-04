#################################  C S V  R E P O R T  G E N E R A T I O N  #################################
from io import StringIO
import csv,io,calendar
from django.core.files.base import ContentFile
from crmAdmin.models import *

def create_report(array, header, header_row, name, admin):
    today = timezone.now().date()
    file_name = header
    with StringIO() as csv_buffer:
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(header_row)
        count = 1
        if name == "followup":
            for emp, status in array:
                csv_writer.writerow([count, emp, status.lead.name, status.lead.phone, status.progress, status.course, status.course.rate, status.notes])
                count +=1
        else:
            for won in array:
                csv_writer.writerow([count, won.employee, won.lead.name, won.lead.phone, won.course, won.course.rate, won.mode])
                count +=1
        csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
    follow_csv = Report.objects.create(name=name, admin=admin)
    follow_csv.csv.save(file_name, csv_file)




# from django.core.management.base import BaseCommand
# from crmAdmin.models import *
# from django.utils import timezone
# from io import StringIO
# import csv,io,calendar
# from django.core.files.base import ContentFile
# from datetime import timedelta, datetime
# from dateutil.relativedelta import relativedelta

# class Command(BaseCommand):
#     help = 'Update Daily'
#     def handle(self, *args, **kwargs):
#         self.followup()
#         self.monthly_rep()

#     # Creating Daily Reports
#     def followup(self):
#         today = timezone.now().date()
#         duty = Duty.objects.filter(lead__lead_status='Yes').order_by('-created_on')
#         list = []
#         for i in duty:
#             leads = leadstatus.objects.filter(leed=i.lead,last_contacted=today).last()
#             if leads:
#                 dut = Duty.objects.get(lead=i.lead)
#                 if dut.sale:
#                     saleperson = dut.sale.user.first_name
#                     list.append((saleperson, leads))
#                 else:
#                     list.append(('Not Asigned', leads))
#         header_row = [
#             '#', 'sale', 'lead', 'lead_number','progress', 'course', 'course_value', 'notes'
#         ]
#         file_name = 'followups '+today.strftime('%Y-%m-%d')+'.csv'
#         with StringIO() as csv_buffer:
#             csv_writer = csv.writer(csv_buffer)
#             csv_writer.writerow(header_row)
#             f=1
#             for j,i in list:
#                 if course.objects.filter(name=i.course).exists():
#                     courses = course.objects.filter(name=i.course).last()
#                     value = courses.rate
#                 else:
#                     value = 0
#                 csv_writer.writerow([f,j,i.leed.name,i.leed.number,i.progress,i.course,value,i.notes])
#                 f +=1
#             csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
#         follow_csv = Report.objects.create(name='followup')
#         follow_csv.csv.save(file_name,csv_file)

#     # Creating Monthly Reports
#     def monthly_rep(self):
#         today = timezone.now().date()
#         start_of_month = today.replace(day=1)
#         if start_of_month.month == 12:
#             end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
#         else:
#             end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)
#         if today == end_of_month:
#             won = Won.objects.filter(won_on__gte=start_of_month,won_on__lte=end_of_month).order_by('-won_on')
#             header_row = [
#                 '#', 'sale', 'lead', 'lead_number', 'course', 'course_value', 'mode'
#             ]
#             file_name = 'monthlywon'+today.strftime('%m')+'.csv'
#             with StringIO() as csv_buffer:
#                 csv_writer = csv.writer(csv_buffer)
#                 csv_writer.writerow(header_row)
#                 f=1
#                 for i in won:
#                     c = course.objects.filter(name=i.course).exists()
#                     if i.course:
#                         c = course.objects.filter(name=i.course).exists()
#                         if c:
#                             courses = course.objects.filter(name=i.course).last()
#                             value = courses.rate
#                         else:
#                             value = 0
#                         csv_writer.writerow([f,i.duty.sale,i.duty.lead.name,i.duty.lead.number,i.course,value,i.mode])
#                     else:
#                         csv_writer.writerow([f,i.duty.sale,i.duty.lead.name,i.duty.lead.number,'course',value,i.mode])
#                     f +=1
#                 csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
#             won_csv = Report.objects.create(name='monthlywon')
#             won_csv.csv.save(file_name,csv_file)
#             duties = Duty.objects.filter(lead__lead_status='Yes').order_by('-created_on')
#             list = []
#             for i in duties:
#                 leads = leadstatus.objects.filter(leed=i.lead,last_contacted__gte=start_of_month,last_contacted__lte=end_of_month).last()
#                 if leads:
#                     dut = Duty.objects.get(lead=i.lead)
#                     if dut:
#                         if dut.sale:
#                             saleperson = dut.sale.user.first_name
#                             list.append((saleperson, leads))
#                         else:
#                             list.append(('Not Asigned', leads))
#             header_row = [
#                 '#', 'sale', 'lead', 'lead_number','progress', 'course', 'course_value', 'notes','date'
#             ]
#             file_name = 'monthlyfollowups'+today.strftime('%m')+'.csv'
#             with StringIO() as csv_buffer:
#                 csv_writer = csv.writer(csv_buffer)
#                 csv_writer.writerow(header_row)
#                 f=1
#                 for j,i in list:
#                     if i.course:
#                         c = course.objects.filter(name=i.course).exists()
#                         if course.objects.filter(name=i.course).exists():
#                             courses = course.objects.filter(name=i.course).last()
#                             value = courses.rate
#                         else:
#                             value = 0
#                         csv_writer.writerow([f,j,i.leed.name,i.leed.number,i.progress,i.course,value,i.notes,i.last_contacted])
#                     f +=1
#                 csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
#             follow_csv = Report.objects.create(name='monthlyfollowup')
#             follow_csv.csv.save(file_name,csv_file)
#             for i in Report.objects.filter(name= 'followup'):
#                 i.delete()

#     ## Creating Monthly Report Code if above doesnt works
#     # def monthly_rep(self):
#     #     today = timezone.now().date()
#     #     start_of_current_month = today.replace(day=1)
#     #     start_of_month = start_of_current_month - relativedelta(months=1)
#     #     if start_of_month.month == 12:
#     #         end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
#     #     else:
#     #         end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)
#     #     if today != end_of_month:
#     #         won = Won.objects.filter(won_on__gte=start_of_month,won_on__lte=end_of_month).order_by('-won_on')
#     #         header_row = [
#     #             '#', 'sale', 'lead', 'lead_number', 'course', 'course_value', 'mode'
#     #         ]
#     #         file_name = 'monthlywon'+today.strftime('%m')+'.csv'
#     #         with StringIO() as csv_buffer:
#     #             csv_writer = csv.writer(csv_buffer)
#     #             csv_writer.writerow(header_row)
#     #             f=1
#     #             for i in won:
#     #                 c = course.objects.filter(name=i.course).exists()
#     #                 if i.course:
#     #                     c = course.objects.filter(name=i.course).exists()
#     #                     if c:
#     #                         courses = course.objects.filter(name=i.course).last()
#     #                         value = courses.rate
#     #                     else:
#     #                         value = 0
#     #                     csv_writer.writerow([f,i.duty.sale,i.duty.lead.name,i.duty.lead.number,i.course,value,i.mode])
#     #                 else:
#     #                     csv_writer.writerow([f,i.duty.sale,i.duty.lead.name,i.duty.lead.number,'course',value,i.mode])
#     #                 f +=1
#     #             csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
#     #         won_csv = Report.objects.create(name='monthlywon')
#     #         won_csv.csv.save(file_name,csv_file)
#     #         duties = Duty.objects.filter(lead__lead_status='Yes').order_by('-created_on')
#     #         list = []
#     #         for i in duties:
#     #             leads = leadstatus.objects.filter(leed=i.lead,last_contacted__gte=start_of_month,last_contacted__lte=end_of_month).last()
#     #             if leads:
#     #                 dut = Duty.objects.get(lead=i.lead)
#     #                 if dut:
#     #                     if dut.sale:
#     #                         saleperson = dut.sale.user.first_name
#     #                         list.append((saleperson, leads))
#     #                     else:
#     #                         list.append(('Not Asigned', leads))
#     #         header_row = [
#     #             '#', 'sale', 'lead', 'lead_number','progress', 'course', 'course_value', 'notes','date'
#     #         ]
#     #         file_name = 'monthlyfollowups'+today.strftime('%m')+'.csv'
#     #         with StringIO() as csv_buffer:
#     #             csv_writer = csv.writer(csv_buffer)
#     #             csv_writer.writerow(header_row)
#     #             f=1
#     #             for j,i in list:
#     #                 if i.course:
#     #                     c = course.objects.filter(name=i.course).exists()
#     #                     if course.objects.filter(name=i.course).exists():
#     #                         courses = course.objects.filter(name=i.course).last()
#     #                         value = courses.rate
#     #                     else:
#     #                         value = 0
#     #                     csv_writer.writerow([f,j,i.leed.name,i.leed.number,i.progress,i.course,value,i.notes,i.last_contacted])
#     #                 f +=1
#     #             csv_file = ContentFile(csv_buffer.getvalue().encode("utf-8"))
#     #         follow_csv = Report.objects.create(name='monthlyfollowup')
#     #         follow_csv.csv.save(file_name,csv_file)
#     #         for i in Report.objects.filter(name= 'followup'):
#     #             i.delete()