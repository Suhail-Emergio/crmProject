from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum, F
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from datetime import timedelta, datetime
from django.shortcuts import render, redirect
from .models import *
from .utils.csv_lead import *
from .utils.assign_utils import *
import calendar
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.lead import Lead
from facebook_business.exceptions import FacebookRequestError
from django.views.decorators.csrf import csrf_exempt

class FacebookLeadAds:
    access_token = settings.FACEBOOK_ACCESS_TOKEN
    app_secret = settings.FACEBOOK_APP_SECRET
    app_id = settings.FACEBOOK_APP_ID

    def __init__(self):
        FacebookAdsApi.init(
            access_token=self.access_token, app_secret=self.app_secret, app_id=self.app_id
        )

    def get_lead_data(self, lead_id):
        try:
            lead = Lead(lead_id).api_get()
        except FacebookRequestError as e:
            return False

        lead_data = lead.get("field_data", None)
        lead_info = {"email": None, "number": None, "name": None}
        for data in lead_data:
            if data.get("name", None) in ["e-mail", "email"]:
                lead_info["email"] = data.get("values")[0].strip().lower()
            elif data.get("name", None) in ["phone_number", "phone"]:
                lead_info["number"] = data.get("values")[0].strip()
            elif data.get("name", None) in ["full_name", "name"]:
                lead_info["name"] = data.get("values")[0].strip()
        return lead_info

@csrf_exempt
def facebook_webhook(request):
    if request.method == 'GET':
        verify_token = request.GET.get("hub.verify_token", "")
        if verify_token == "EMERGIO_WEBHOOK_LEADS":
            challenge = request.GET.get("hub.challenge", 0)
            return HttpResponse(int(challenge))
        return HttpResponseForbidden("Wrong verification token")

    elif request.method == 'POST':
        entry = request.POST.get("entry", None)
        for data in entry:
            changes = data["changes"]
            for change in changes:
                leadgen_id = change["value"]["leadgen_id"]
                lead_data = FacebookLeadAds().get_lead_data(leadgen_id)
                if lead_data and lead_data.get("email") and lead_data.get("number") and lead_data.get("name"):
                    lead_email = lead_data.get("email")
                    lead_number = lead_data.get("number")
                    lead_name = lead_data.get("name")
                    Lead.objects.create(email=lead_email, number=lead_number, name=lead_name, campain=True)
        return HttpResponse({"success": True})

# Dashboard
@login_required(login_url='login')
def dash(request):
    if request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.filter(admin=request.user,trash=False)[:4]
        sale = Employee.objects.filter(admin=request.user)[:4]
        courses = Course.objects.all()[:4]
        payments = Payment.objects.all()[:4]
        callbacks = Callback.objects.all().order_by('date')[:4]
        leads_won  = Won.objects.filter(lead__admin = request.user).annotate(month=ExtractMonth("won_on")).values("month").annotate(count=Count("id")).values("month", "count")[:3]
        return render(request,'admin/dashboard.html',{'lead':lead,'sale':sale,'course':courses,'payment':payments,'callback':callbacks,'won':leads_won})
    return redirect('login')

# Leads
@login_required(login_url='login')
def leads(request):
    if request.user and request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.filter(admin=request.user, trash=False, campain=False).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(lead, 25)
        leads = paginator.get_page(page)
        count = Lead.objects.filter(admin=request.user, trash=False, campain=False).count()
        if request.method == "POST":
            csv_fetch(request.FILES['file'], request.user)
            return redirect('lead')
        return render(request,"admin/leed.html",{'lead':leads,'count':count})
    return redirect('login')

# Campain Leads
@login_required(login_url='login')
def campain_leads(request):
    if request.user and request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.filter(admin=request.user, trash=False, campain=True).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(lead, 25)
        leads = paginator.get_page(page)
        count = Lead.objects.filter(admin=request.user, trash=False, campain=True).count()
        if request.method == "POST":
            csv_fetch(request.FILES['file'], request.user)
            return redirect('lead')
        return render(request,"admin/campain_leads.html",{'lead':leads,'count':count})
    return redirect('login')

# Edit Lead details
@login_required(login_url='login')
def edit_lead(request,id):
    if request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.get(id=id)
        if request.method == 'POST':
            lead.name = request.POST.get('name')
            lead.number = request.POST.get('number')
            lead.email=request.POST.get('email')
            lead.watsapp = request.POST.get('wpno')
            lead.department = request.POST.get('department')
            lead.save()
            return redirect('lead')
        return render(request, "admin/edit_lead.html", {'lead': lead})
    return redirect('login')

# Deleting Lead
@login_required(login_url='login')
def del_lead(request,id):
    if request.user.type == "admin" and not request.user.block:
        lead=Lead.objects.get(id=id)
        if lead.won_set.exists() or lead.payment_set.exists():
            messages.error(request, "Cannot delete this lead because it is referenced by other records (e.g., Won or Payment).")
        else:
            lead.delete()
        return redirect('lead')
    return redirect('login')

# View Leads Status
@login_required(login_url='login')
def lead_status(request,id):
    if request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.get(id=id)
        status = Leadstatus.objects.filter(lead=lead).order_by('-id')
        if Duty.objects.filter(lead=lead).exists():
            duty = Duty.objects.get(lead=lead)
            sale = duty.emp
            calls = Callback.objects.filter(duty=duty)
            resp ={'lead_status':status,'lead':lead,'calls':calls,'sale':sale}
        else:
            resp ={'lead_status':status,'lead':lead}
        return render(request, "admin/lead_status.html",resp)
    return redirect('login')

# View Employees
@login_required(login_url='login')
def employee(request):
    if request.user.type == "admin" and not request.user.block:
        emp = Employee.objects.filter(admin=request.user,user__block=False).order_by('-id')
        count = Employee.objects.filter(admin=request.user,user__block=False).count()
        if request.method == 'POST':
            phone = request.POST.get('number')
            name = request.POST.get('name')
            email = ""
            password = request.POST.get('password')
            strength = request.POST.get('strength')
            type = "employee"
            if UserInfo.objects.filter(phone=phone).exists():
                return redirect('admin_employee')
            user = UserInfo.objects.create(phone=phone,name=name,email=email,type=type)
            user.set_password(password)
            user.save()
            person = Employee.objects.create(user=user,strength=strength,admin=request.user)
            person.save()

            ## Daily and Monthly Target
            target = Target(sale=Employee.objects.get(user = user), type = "Monthly", target = request.POST.get('mon_tar'), target_remaining = request.POST.get('mon_tar'),
                        target_won = 0, date=timezone.now())
            target.save()
            target = Target(sale=Employee.objects.get(user = user), type = "Daily", target = request.POST.get('daily_tar'), target_remaining = request.POST.get('daily_tar'),
                        target_won = 0, date=timezone.now())
            target.save()
            return redirect('admin_employee')
        return render(request, "admin/salespersons.html", {'person': emp,'count':count})
    return redirect('login')

# View Employees
@login_required(login_url='login')
def blocked_emp(request):
    if request.user.type == "admin" and not request.user.block:
        emp = Employee.objects.filter(admin=request.user,user__block=True).order_by('-id')
        count = Employee.objects.filter(admin=request.user,user__block=True).count()
        return render(request, "admin/blocked_emp.html", {'person': emp,'count':count})
    return redirect('login')

# Edit Employees
@login_required(login_url='login')
def edit_emp(request,id):
    if request.user.type == "admin" and not request.user.block:
        lead = Employee.objects.get(id=id)
        user = lead.user
        if request.method == 'POST':
            user.name = request.POST.get('name')
            user.phone = request.POST.get('number')
            lead.strength = request.POST.get('strength')
            lead.target = request.POST.get('target')
            if request.POST.get('password'):
                user.set_password(request.POST.get('password'))
            user.save()
            lead.save()
            return redirect('admin_employee')
        return render(request, "admin/edit_sales.html", {'lead': lead})
    return redirect('login')

# Delete Sales
@login_required(login_url='login')
def del_emp(request,id):
    if request.user.type == "admin" and not request.user.block:
        emp = Employee.objects.get(id=id)
        user=UserInfo.objects.get(id=emp.user.id)
        user.delete()
        return redirect('admin_employee')
    return redirect('login')

# Duty
@login_required(login_url='login')
def duty(request,id):
    if request.user.type == "admin" and not request.user.block:
        person1 = Employee.objects.get(id=id)
        duty = Duty.objects.filter(emp=person1).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(duty, 25)
        duties = paginator.get_page(page)
        target = Target.objects.filter(sale=person1,type="Monthly").order_by('-id').annotate(month=ExtractMonth("date")).values("month").annotate(target_won=Sum('target_won'),target=Sum('target'),target_remaining=F('target') - F('target_won')).values("month", "target_won","target","target_remaining")
        daily = Target.objects.filter(sale=person1,type="Daily").order_by('-id').annotate(month=ExtractMonth("date")).values('month').annotate(target_won=Sum('target_won'),target=Sum('target'),target_remaining=F('target') - F('target_won')).values("date", "target_won","target","target_remaining")

        if 'quality' in request.POST:
            date = datetime.now().month
            targets = Target.objects.filter(sale=person1,date__month=date,type="Daily")
            if targets.exists():
                for i in targets:
                    i.target = request.POST.get('qualities')
                    i.target_remaining = int(i.target) - int(i.target_won)
                    i.save()
            else:
                target = request.POST.get('qualities')
                target_won = 0
                target = Daily_Target(sale=saleperson.objects.get(id=person),target=target,target_remaining=target,target_won=target_won,date=timezone.now())
                target.save()
            return redirect('duty',id=id)
        return render(request, "admin/duty.html",{'duty':duties,'person1':person1,'data':target,'daily':daily})
    return redirect('login')

# Daily Targets
@login_required(login_url='login')
def daily(request):
    person1 = Employee.objects.get(id=request.POST.get('user'))
    current_month = datetime.now().date()
    targets = Target.objects.filter(sale=person1,date=current_month,type="Daily")
    if targets.exists():
        for i in targets:
            i.target = request.POST.get('qualities')
            i.target_remaining = int(i.target) - int(i.target_won)
            i.save()
    else:
        target = request.POST.get('qualities')
        target_won = 0
        target = Target(sale=person1,target=target,target_remaining=target,target_won=target_won,date=timezone.now(),type="Daily")
        target.save()
    return redirect('duty',id=request.POST.get('user'))

# Monthly Targets
@login_required(login_url='login')
def monthly(request):
    person1 = Employee.objects.get(id=request.POST.get('user'))
    current_month = datetime.now().month
    if Target.objects.filter(sale=person1,date__month=current_month,type="Monthly").exists():
        targets = Target.objects.get(sale=person1,date__month=current_month,type="Monthly")
        targets.target = request.POST.get('target')
        targets.target_remaining = int(i.target) - int(i.target_won)
        targets.save()
    else:
        target = request.POST.get('target')
        target = Target(sale=person1,target=target,target_remaining=target,target_won=0,date=timezone.now(),type="Monthly")
        target.save()
    return redirect('duty',id=request.POST.get('user'))

# Deleting a Duty
@login_required(login_url='login')
def del_duty(request,id):
    if request.user.type == "admin" and not request.user.block:
        duty = Duty.objects.get(id=id)
        duty.delete()
        return redirect('admin_employee')
    return redirect('login')

# Assignable Leads
@login_required(login_url='login')
def assign(request):
    if request.user.type == "admin" and not request.user.block:
        assign = Lead.objects.filter(admin=request.user, assign_status=False, trash=False)
        count = Lead.objects.filter(admin=request.user, assign_status=False, trash=False).count()
        emp = Employee.objects.filter(admin=request.user, strength__gt=0)
        return render(request,"admin/assign_duty.html",{'assign':assign, 'count':count, 'emp':emp})
    return redirect('login')

# Assign
@login_required(login_url='login')
def assign_lead(request,id):
    lead = Lead.objects.get(id=id)
    if request.method == "POST":
        employee = Employee.objects.get(id=request.POST.get('employee_id'))
        duty = Duty.objects.create(lead=lead,emp=employee,delete_date=(timezone.now().date() + timedelta(days=1)))
        duty.save()
        employee.todays_lead += 1
        employee.total_lead += 1
        employee.save()
        lead.assign_status = True
        lead.save()
        return redirect('assign')

# Assign All
@login_required(login_url='login')
def assign_all_lead(request):
    if request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.filter(admin = request.user, assign_status = False, trash=False, lead_status=False)
        for i in lead:
            assign_leads(i)
        other_leads = Lead.objects.filter(admin = request.user, assign_status = False, trash=False)
        for i in other_leads:
            assign_leads(i)
        return redirect('assign')
    return redirect('login')

# Courses
@login_required(login_url='login')
def courses(request):
    if request.user.type == "admin" and not request.user.block:
        courses=Course.objects.all().order_by('-id')
        if request.method == 'POST':
            syllabus = request.FILES['syllabus']
            course = Course.objects.create(
                name=request.POST.get('name'),
                duration=request.POST.get('course'),
                internship=request.POST.get('internship'),
                rate=request.POST.get('rate'),
                gst=request.POST.get('gst'),
                total_rate=int(request.POST.get('rate'))+(int(request.POST.get('rate'))*(int(request.POST.get('gst'))/100)),
                syllabus=syllabus
            )
            course.save()
            return redirect('course')
        return render(request,"admin/course.html",{'courses':courses})
    return redirect('login')

# Edit Courses
@login_required(login_url='login')
def edit_course(request, id):
    if request.user.type == "admin" and not request.user.block:
        courses=Course.objects.get(id=id)
        if request.method == 'POST':
            courses.name = request.POST.get('name')
            courses.duration = request.POST.get('duration')
            courses.internship = request.POST.get('internship')
            courses.rate = request.POST.get('rate')
            courses.gst = request.POST.get('gst')
            total_rate = int(courses.rate)+(int(courses.rate)*(int(courses.gst)/100))
            courses.total_rate = int(total_rate)
            if 'check' in request.POST:
                courses.syllabus = request.FILES['syllabus']
            courses.save()
            return redirect('course')
        return render(request,'admin/edit_course.html',{'courses':courses})
    return redirect('login')

# Delete Course
@login_required(login_url='login')
def del_course(request, id):
    if request.user.type == "admin" and not request.user.block:
        courses = Course.objects.get(id=id)
        courses.delete()
        return redirect('course')
    return redirect('login')

# Follow Ups
@login_required(login_url='login')
def followup(request):
    if request.user.type == "admin" and not request.user.block:
        duty = Duty.objects.filter(lead__lead_status=True, lead__admin=request.user).order_by('-created_on')
        list =[]
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead).last()
            if leads:
                list.append(leads)
        page = request.GET.get('page', 1)
        paginator = Paginator(list, 25)
        lists = paginator.get_page(page)
        return render(request, 'admin/followups.html', {'duty': lists})
    return redirect('login')

# Payments
@login_required(login_url='login')
def payments(request):
    if request.user.type == "admin" and not request.user.block:
        payment = Payment.objects.filter(lead__admin=request.user)
        return render(request,"admin/payment.html",{'payments':payment})
    return redirect('login')

# Callbacks
@login_required(login_url='login')
def callbacks(request):
    if request.user.type == "admin" and not request.user.block:
        calls = Callback.objects.filter(duty__lead__admin=request.user)
        page = request.GET.get('page', 1)
        paginator = Paginator(calls, 25)
        call = paginator.get_page(page)
        return render(request,"admin/callback.html",{'calls':call})
    return redirect('login')

# Won Leads
@login_required(login_url='login')
def won(request):
    if request.user.type == "admin" and not request.user.block:
        won = Won.objects.filter(lead__admin = request.user).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(won, 25)
        wons = paginator.get_page(page)
        return render(request, "admin/leads_won.html",{'won':wons})
    return redirect('login')

# Edit Profile
@login_required(login_url='login')
def settings(request):
    user = request.user
    if request.method == 'POST':
        if 'name' in request.POST:
            user.phone = request.POST.get('username')
        if 'fname' in request.POST:
            user.name = request.POST.get('names')
        if 'pass' in request.POST:
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            return redirect('login')
        user.save()
        return redirect('settings')
    return render(request, "admin/settings.html",{'superusers':user})

# Delete account
@login_required(login_url='login')
def del_suser(request,id):
    user = request.user
    user.delete()
    return redirect('settings')

# Reports View
@login_required(login_url='login')
def reports(request):
    if request.user.type == "admin" and not request.user.block:
        report = Report.objects.filter(name='followup', admin=request.user)
        won = Report.objects.filter(name='monthly_won', admin=request.user)
        followup = Report.objects.filter(name='monthly_followup', admin=request.user)
        sr = SaleReport.objects.filter(emp__admin=request.user, date=datetime.now().date())
        return render(request, 'admin/reports.html',{'report':report,'won':won,'followup':followup, "sr":sr})
    return redirect('login')

# Not Answered Leads
@login_required(login_url='login')
def not_answered(request):
    if request.user.type == "admin" and not request.user.block:
        assign = TrashLead.objects.filter(lead__admin=request.user ,lost=False)
        return render(request, 'admin/notanswer.html',{'assign':assign})
    return redirect('login')

# Trash Leads
@login_required(login_url='login')
def trash_leads(request):
    if request.user.type == "admin" and not request.user.block:
        assign = TrashLead.objects.filter(lead__admin = request.user ,lost=True)
        return render(request, 'admin/trash.html',{'assign':assign})
    return redirect('login')

# Recover Trash Leads
@login_required(login_url='login')
def recover_lead(request,id):
    if request.user.type == "admin" and not request.user.block:
        lead = Lead.objects.get(id=id)
        lead.trash = False
        lead.save()
        trash = TrashLead.objects.get(lead=lead)
        trash.delete()
        return render(request, 'admin/trash.html',{'assign':assign})
    return redirect('login')

# Return month name
def get_month_name(month_number):
    return calendar.month_name[month_number]

# Privacy Policy Page
def privacy(request):
    return render(request, 'privacypolicy.html')