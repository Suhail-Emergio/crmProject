from datetime import timedelta, datetime
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.db.models import Count, Sum, F
from django.db.models.functions import ExtractMonth
from django.shortcuts import render, redirect
from crmAdmin.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Dashboard
@login_required(login_url='login')
def dash(request):
    if request.user.type == "superadmin":
        todays_sales = Won.objects.filter(won_on = datetime.now().date()).aggregate(sum=Sum("course__rate"))
        total_sales = Won.objects.all().aggregate(sum=Sum("course__rate"))
        total_emp = Employee.objects.all().count()
        total_lead = Lead.objects.all().count()
        leads_won  = Won.objects.annotate(month=ExtractMonth("won_on")).values("month").annotate(count=Count("id")).values("month", "count")
        emp_sales = Won.objects.values('employee__user__name').annotate(total_sales=Sum('course__rate')).annotate(count=Count("id"))
        callback = Callback.objects.filter(date = datetime.now().date()).values('duty__emp__user__name').annotate(count=Count("id"))
        return render(request,'superuser/dashboard.html' ,{
            'todays_sales' : todays_sales,
            'total_emp' : total_emp,
            'total_lead' : total_lead,
            'total_sales' : total_sales,
            'leads_won' : leads_won,
            'emp_sales' : emp_sales,
            'callback' : callback,
        })
    return redirect('login')

# Admins
@login_required(login_url='login')
def admins(request):
    if request.user.type == "superadmin":
        admin = Admins.objects.filter(user__block = False).order_by('-id')
        title = "Admins"
        return render(request,'superuser/admins.html', {'admin':admin, 'title':title})
    return redirect('login')

# Banned Admins
@login_required(login_url='login')
def banned_admins(request, action):
    if request.user.type == "superadmin":
        if action == 'ban':
            admin = Admins.objects.filter(user__block = True).order_by('-id')
            title = "Banned Admins"
            return render(request,'superuser/admins.html', {'admin':admin, 'title':title})
    return redirect('login')

# Create Admins
@login_required(login_url='login')
def create_admin(request):
    if request.user.type == "superadmin":
        if request.method == "POST":
            if UserInfo.objects.filter(phone=request.POST['phone']).exists():
                messages.error(request,"User with this phone number already exists")
            else:
                user = UserInfo.objects.create_user(
                    name = request.POST['name'].capitalize(),
                    email = request.POST['email'],
                    password = request.POST['password'],
                    phone = request.POST['phone'],
                    type = "admin"
                )
                user.save()
                admin = Admins.objects.create(
                    user = user,
                    superadmin = request.user,
                    target = request.POST['target']
                )
                admin.save()
            return redirect('admin')
    return redirect('login')

# Edit Admins
@login_required(login_url='login')
def edit_admin(request, id):
    if request.user.type == "superadmin":
        admin = Admins.objects.get(id = id)
        if request.method == "POST":
            if admin.user.phone != request.POST['phone'] and UserInfo.objects.filter(phone=request.POST['phone']).exists():
                messages.error(request,"User with this phone number already exists")
            else:
                user = admin.user
                user.name = request.POST['name'].capitalize()
                user.email = request.POST['email']
                if request.POST['password'] != '':
                    user.set_password(request.POST['password'])
                user.phone = request.POST['phone']
                user.save()
            return redirect('admin')
    return redirect('login')

# Delete Admins
@login_required(login_url='login')
def delete_admin(request, id):
    if request.user.type == "superadmin":
        admin = Admins.objects.get(id = id)
        admin.user.delete()
        return redirect('admin')
    return redirect('login')

# Employees
@login_required(login_url='login')
def employees(request):
    if request.user.type == "superadmin":
        employee = Employee.objects.filter(user__block = False).order_by('-id')
        title = "Employees"
        return render(request,'superuser/employees.html', {'employee':employee, 'title':title})
    return redirect('login')

# Duties of an employee
@login_required(login_url='login')
def emp_duty(request, id):
    if request.user.type == "superadmin":
        person1 = Employee.objects.get(id=id)
        duty = Duty.objects.filter(emp=person1).order_by('-id')
        target = Target.objects.filter(sale=person1,type="Monthly").order_by('-id').annotate(month=ExtractMonth("date")).values("month").annotate(target_won=Sum('target_won'),target=Sum('target'),target_remaining=F('target') - F('target_won')).values("month", "target_won","target","target_remaining")
        daily = Target.objects.filter(sale=person1,type="Daily").order_by('-id').annotate(month=ExtractMonth("date")).values('month').annotate(target_won=Sum('target_won'),target=Sum('target'),target_remaining=F('target') - F('target_won')).values("date", "target_won","target","target_remaining")
        return render(request, "superuser/emp_duty.html",{'duty':duty,'person1':person1,'data':target,'daily':daily})

# Duties of an Admin
@login_required(login_url='login')
def admin_duty(request, id):
    if request.user.type == "superadmin":
        admin = Admins.objects.get(id=id)
        employee = Employee.objects.filter(admin=admin.user).order_by('-id')
        won = Won.objects.filter(lead__admin=admin.user).order_by('-id')
        lead = Lead.objects.filter(admin=admin.user).exclude(closed=True).order_by('-id')
        return render(request, "superuser/admin_duty.html",{'employee':employee,'admin':admin,'won':won,'lead':lead})

# Banned Employees
@login_required(login_url='login')
def banned_employee(request, action):
    if request.user.type == "superadmin":
        if action == 'ban':
            employee = Employee.objects.filter(user__block = True).order_by('-id')
            title = "Banned Employees"
            return render(request,'superuser/employees.html', {'employee':employee, 'title':title})
    return redirect('login')

# Delete Employees
@login_required(login_url='login')
def delete_employee(request, id):
    if request.user.type == "superadmin":
        emp = Employee.objects.get(id = id)
        emp.user.delete()
        return redirect('employee')
    return redirect('login')

# Leads
@login_required(login_url='login')
def leads(request):
    if request.user.type == "superadmin":
        page = request.GET.get('page', 1)
        lead = Lead.objects.filter(campain=False).order_by('-id')
        paginator = Paginator(lead, 25)
        leads = paginator.get_page(page)
        return render(request, 'superuser/leads.html', {"lead": leads})
    return redirect('login')

# Campain Leads
@login_required(login_url='login')
def campain_leads(request):
    if request.user.type == "superadmin":
        page = request.GET.get('page', 1)
        leads = Lead.objects.filter(campain=True).order_by('-id')
        paginator = Paginator(leads, 25)
        leads = paginator.get_page(page)
        return render(request, 'superuser/campain_leads.html', {"lead": leads})
    return redirect('login')

# Leads Status
@login_required(login_url='login')
def status(request, id):
    if request.user.type == "superadmin":
        status = Leadstatus.objects.filter(lead__id = id).order_by('-id')
        name = Lead.objects.get(id=id).name
        employee = Duty.objects.get(lead__id=id).emp if Duty.objects.filter(lead__id=id).exists() else None
        return render(request,'superuser/status.html', {'status':status, 'name':name, "employee":employee})
    return redirect('login')

# Leads
@login_required(login_url='login')
def follows(request):
    if request.user.type == "superadmin":
        duty = Duty.objects.filter(lead__lead_status=True).order_by('-created_on')
        list = []
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead).last()
            if leads:
                list.append((leads,i.emp))
        page = request.GET.get('page', 1)
        paginator = Paginator(list, 25)
        lists = paginator.get_page(page)
        return render(request,'superuser/followup.html',{"lead":lists})
    return redirect('login')

# Won
@login_required(login_url='login')
def wons(request):
    if request.user.type == "superadmin":
        won = Won.objects.all().order_by('-won_on')
        page = request.GET.get('page', 1)
        paginator = Paginator(won, 25)
        wons = paginator.get_page(page)
        return render(request,'superuser/won.html', {'won':wons})
    return redirect('login')

# Payments
@login_required(login_url='login')
def payment(request):
    if request.user.type == "superadmin":
        pays = Payment.objects.all().order_by('-id')
        return render(request,'superuser/payment.html', {'payment':pays})
    return redirect('login')

# Callbacks
@login_required(login_url='login')
def callbacks(request):
    if request.user.type == "superadmin":
        page = request.GET.get('page', 1)
        callback = Callback.objects.all().order_by('-id')
        paginator = Paginator(callback, 25)
        callbacks = paginator.get_page(page)
        return render(request,'superuser/callback.html', {'callback':callbacks})
    return redirect('login')

# Not Answered Leads
@login_required(login_url='login')
def naleads(request):
    if request.user.type == "superadmin":
        nalead = TrashLead.objects.filter(lost=False).order_by('-id')
        return render(request,'superuser/naleads.html', {'nalead':nalead})
    return redirect('login')

# Admins in reports
@login_required(login_url='login')
def reports_admin(request):
    if request.user.type == "superadmin":
        admin = Admins.objects.filter(user__block = False).order_by('-id')
        return render(request,'superuser/report.html', {'admin':admin})
    return redirect('login')

# Reports of an admin
@login_required(login_url='login')
def report(request, id):
    if request.user.type == "superadmin":
        report = Report.objects.filter(name='followup', admin__id=id).order_by('-id')
        won = Report.objects.filter(name='monthly_won', admin__id=id).order_by('-id')
        followup = Report.objects.filter(name='monthly_followup', admin__id=id).order_by('-id')
        name = UserInfo.objects.get(id=id).name
        sreport = SaleReport.objects.filter(emp__admin__id=id, date=datetime.now().date())
        return render(request,'superuser/reportspage.html', {'report':report, 'won':won, 'followup':followup, 'name':name, 'sr': sreport})
    return redirect('login')