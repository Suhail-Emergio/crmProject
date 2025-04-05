from datetime import timedelta, datetime, date
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.shortcuts import render, redirect
from crmAdmin.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Dashboard of Employee
@login_required(login_url='login')
def home(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.get(user=user)
        duty = Duty.objects.filter(emp=sale, lead__lead_status=False, lead__trash=False).order_by('-created_on')[:4]
        calls = Callback.objects.filter(duty__emp=sale)[:4]
        courses = Course.objects.all()
        callbacks = Callback.objects.filter(duty__emp=sale).count()
        total_duty = Duty.objects.filter(emp=sale).count()
        total_won = Won.objects.filter(employee=sale).count()
        completed = Duty.objects.filter(emp=sale, lead__lead_status=True,lead__closed=False, created_on=datetime.now()).count()
        uncompleted = Duty.objects.filter(emp=sale, lead__lead_status=False,lead__trash=False, created_on=datetime.now()).count()
        wons = Won.objects.filter(employee=sale, won_on=datetime.now()).count()
        leads_won = Won.objects.filter(employee=sale).annotate(month=ExtractMonth("won_on")).values("month").annotate(
            count=Count("id")).values("month", "count")[:3]
        callbacks_today  = []
        for i in Callback.objects.filter(duty__emp=sale, date = timezone.now().date()):
            callbacks_today.append(i.duty.lead)
        current_month = datetime.now().month
        target = Target.objects.filter(sale=sale, date__month=current_month, type="Monthly").first()
        daily = Target.objects.filter(sale=sale, date=datetime.now(), type="Daily").first()
        yesterday = Target.objects.filter(sale=sale, date__month=current_month, type="Daily").first()
        return render(request, 'user/index.html',
        {'duty': duty, 'calls': calls,'callbacks_today': callbacks_today, 'courses': courses, 'completed': completed,'l_won':wons,'daily':daily,
        'uncompleted': uncompleted, 'won': leads_won,'total_duty':total_duty,'callbacks':callbacks,'total_won':total_won,'target':target})
    return redirect('login')

# Leads assigned to an Employee
@login_required(login_url='login')
def lead(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=False, lead__closed=False, lead__trash=False, lead__campain=False, lead__quality=False).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(duty, 25)
        duties = paginator.get_page(page)

        ## Adding Reference
        if request.method == 'POST':
            name = request.POST.get('name')
            number = request.POST.get('number')
            if Lead.objects.filter(phone=number).exists():
                dut = Duty.objects.get(lead__phone=number)
                message = f"Lead already exists. Asssigned to : {dut.sale}"
                messages.error(request, message)
                return redirect('user_lead')
            leads = Lead.objects.create(name=name, phone=number,assign_status=True,admin=sale.admin)
            leads.save()
            duty = Duty.objects.create(emp=sale, lead=Lead.objects.get(phone=number), delete_date=(timezone.now().date() + timedelta(days=1)))
            duty.save()
            return redirect('user_lead')
        return render(request, 'user/leads.html', {'duty': duties})
    return redirect('login')

# Leads assigned to an Employee
@login_required(login_url='login')
def campain_lead(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        start_date_str = request.GET.get('start_date', '').strip()
        end_date_str = request.GET.get('end_date', '').strip()
        if not start_date_str or not end_date_str:
            start_date = date.today()
            end_date = date.today()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=False, lead__closed = False, lead__trash=False, lead__campain=True, lead__created_on__range=[start_date, end_date], lead__quality=False).order_by('-created_on')
        page = request.GET.get('page', 1)
        paginator = Paginator(duty, 25)
        duties = paginator.get_page(page)
        return render(request, 'user/campain_leads.html', {'duty': duties})
    return redirect('login')

@login_required(login_url='login')
def quality_followups(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=True, lead__closed = False, lead__quality = True).order_by('-created_on')
        list =[]
        current_month = datetime.now().month
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead, contacted_on__month=current_month).last()
            if leads:
                list.append(leads)
        page = request.GET.get('page', 1)
        paginator = Paginator(list, 25)
        lists = paginator.get_page(page)
        return render(request, 'user/quality_follows.html', {'duty': lists})
    return redirect('login')
# Lead status
@login_required(login_url='login')
def status(request, id):
    if request.user.type == "employee" and not request.user.block:
        lead = Lead.objects.get(id=id)
        status = Leadstatus.objects.filter(lead__id=id).order_by('-id')
        courses = Course.objects.all()
        payments = Payment.objects.filter(lead=lead)
        if 'statuses' in request.POST:
            progress = request.POST.get('progress')
            stats = request.POST.get('status')
            notes = request.POST.get('notes')
            probability = request.POST.get('probability')
            course = Course.objects.get(id=request.POST.get('courses')) if request.POST.get('courses') else None
            duty = Duty.objects.get(lead=lead)
            status = Leadstatus.objects.create(lead=lead, status=stats, progress=progress, notes=notes, probability=probability, course=course)
            status.save()
            if duty:
                report = SaleReport.objects.filter(date=date.today(), emp__user=request.user).last()
                if not report:
                    report = SaleReport.objects.create(emp=duty.emp)
                if stats == 'Follow Up':
                    print("djfcxnkl")
                    lead.lead_status = True 
                    if request.POST.get('quality'):
                        lead.quality = True
                        lead.save()
                    call_date = request.POST.get('date')
                    if Callback.objects.filter(duty=duty).exists():
                        callbacks = Callback.objects.get(duty=duty)
                        callbacks.delete()
                    calls = Callback.objects.create(duty=duty, date=call_date)
                    calls.save()
                    report.follow += 1
                elif stats == 'Quality':
                    lead.lead_status=True
                    if request.POST.get('quality'):
                        lead.quality = True
                        lead.save()
                elif stats == 'Won':
                    won = Won.objects.create(lead=lead, employee=Employee.objects.get(user=request.user), course=Course.objects.get(id=request.POST.get('course')), mode=request.POST.get('mode'),type=request.POST.get('type'))
                    won.save()
                    payments = Payment.objects.create(lead=lead, rate=request.POST.get('rate'), screenshot=request.FILES['ss'])
                    payments.save()
                elif stats == "Lost":
                    report.Notinterested += 1
                else: 
                    report.Notanswer += 1
                report.save()
                lead.save()
            return redirect('status', id=id)
        return render(request, "user/leadstatus.html", {'leed': lead, 'status': status, 'course': courses, 'payment': payments})
    return redirect('login')

# Follow ups
@login_required(login_url='login')
def followups(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=True,lead__trash=False, lead__closed = False, lead__campain=False, lead__quality=False).order_by('-created_on')
        list =[]
        current_month = datetime.now().month
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead).last()
            if leads:
                list.append(leads)
        return render(request, 'user/followups.html', {'duty': list})
    return redirect('login')

# Campain Follow ups
@login_required(login_url='login')
def campain_followups(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=True, lead__trash=False, lead__closed = False, lead__campain=True, lead__quality=False).order_by('-created_on')
        list =[]
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead).last()
            if leads:
                list.append(leads)
        return render(request, 'user/campain_follows.html', {'duty': list})
    return redirect('login')

# Total follow ups
@login_required(login_url='login')
def totalfollow(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        sale = Employee.objects.filter(user=user).first()
        duty = Duty.objects.filter(emp=sale, lead__lead_status=True,lead__closed = False).order_by('-created_on')
        list =[]
        for i in duty:
            leads = Leadstatus.objects.filter(lead=i.lead).last()
            if leads:
                list.append(leads)
        return render(request, 'user/totalfollow.html', {'duty': list})
    return redirect('login')

# Won leads
@login_required(login_url='login')
def leads_won(request):
    if request.user.type == "employee" and not request.user.block:
        user = request.user
        won = Won.objects.filter(employee__user=user).order_by('-id')
        return render(request, 'user/won.html', {'duty': won})
    return redirect('login')

# Callbacks
@login_required(login_url='login')
def callbacks(request):
    if request.user.type == "employee" and not request.user.block:
        calls = Callback.objects.filter(duty__emp__user=request.user, status=False).order_by('date')
        return render(request, 'user/callbacks.html', {'calls': calls})
    return redirect('login')

# Courses
@login_required(login_url='login')
def syllabus(request):
    if request.user.type == "employee" and not request.user.block:
        courses = Course.objects.all()
        return render(request, 'user/syllabus.html', {'courses': courses})
    return redirect('login')

@login_required(login_url='login')
def salereports(request):
    if request.user.type == "employee" and not request.user.block:
        report = SaleReport.objects.filter(emp__user=request.user)
        tod = timezone.now().date()
        return render(request, 'user/reports.html', {'report': report,'tod':tod})
    return redirect('login')