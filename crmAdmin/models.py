from django.contrib.auth.models import User
from django.db import models
from user.models import *

# Admin
class Admins(models.Model):
    superadmin = models.ForeignKey(UserInfo,on_delete=models.CASCADE, related_name="superadmin")
    user = models.ForeignKey(UserInfo,on_delete=models.CASCADE, related_name="admin")
    target = models.IntegerField()
    target_won = models.IntegerField(default=0)

    def __str__(self):
        return self.user.name

# Employee
class Employee(models.Model):
    admin = models.ForeignKey(UserInfo,on_delete=models.CASCADE, related_name="employee_admin")
    user = models.ForeignKey(UserInfo,on_delete=models.CASCADE, related_name="user")
    strength = models.IntegerField()
    total_lead = models.IntegerField(default=0)
    todays_lead = models.IntegerField(default=0)
    campain_leads = models.IntegerField(default=0)

    def __str__(self):
        return self.user.name

# Target of a user
class Target(models.Model):
    type = models.CharField(max_length=100, choices=[('Daily', 'Daily'), ('Monthly', 'Monthly')])
    sale = models.ForeignKey(Employee, on_delete=models.CASCADE)
    target = models.IntegerField()
    target_won = models.IntegerField(default=0)
    target_remaining = models.IntegerField(default=0)
    date = models.DateField()

# Courses
class Course(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField()
    internship = models.CharField(max_length=100)
    rate = models.IntegerField()
    gst = models.IntegerField()
    total_rate = models.IntegerField()
    syllabus = models.FileField(upload_to='course/')

    def __str__(self):
        return self.name

# Leads
class Lead(models.Model):
    admin = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100)
    department = models.CharField(max_length=100, null=True, blank=True)
    assign_status = models.BooleanField(default=False)
    lead_status = models.BooleanField(default=False)
    campain = models.BooleanField(default=False)
    quality = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)
    created_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

# Duties
class Duty(models.Model):
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    delete_date = models.DateField()
    created_on = models.DateField(auto_now=True)

    def __str__(self):
       return self.lead.name

# Lead Status
class Leadstatus(models.Model):
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE)
    progress = models.CharField(max_length=100,choices=[('Not Contacted Yet', 'Not Contacted Yet'), ('Not Answering', 'Not Answering'),('Busy', 'Busy'),('Contacted', 'Contacted:Waiting For Reply'),('Got Appointment', 'Got Appointment'),('Payment', 'Payment'),('Not Interested', 'Not Interested'),('Quality','Quality'),('Invalid number','Invalid number')],default='Not Contacted Yet')
    status = models.CharField(max_length=100,choices=[('Not Answering', 'Not Answering'),('Follow Up', 'Follow Up'), ('Won', 'Won'),('Lost', 'Lost'),('Quality','Quality')],default='Not Answering')
    probability = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField()
    contacted_on = models.DateField(auto_now=True)

# Callbacks
class Callback(models.Model):
    duty = models.ForeignKey(Duty, on_delete=models.CASCADE, related_name='duty')
    date = models.DateField()
    note = models.TextField()
    status = models.BooleanField(default=False)

# Won Info
class Won(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.PROTECT)
    employee =  models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    mode = models.CharField(max_length=100,choices=[('Course', 'Course'), ('Internship', 'Internship')])
    type = models.CharField(max_length=100, choices=[('Online', 'Online'), ('Offline', 'Offline')])
    won_on = models.DateField(auto_now=True)

# Payments
class Payment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.PROTECT)
    rate = models.CharField(max_length=100)
    screenshot = models.FileField(upload_to='media/')

# Reports
class Report(models.Model):
    admin = models.ForeignKey(UserInfo,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    csv = models.FileField(upload_to='report')
    created_on = models.DateField(auto_now=True)

    def _str_(self):
        return f"{self.name} - {self.created_on}"

# Sales Reports
class SaleReport(models.Model):
    date = models.DateField(auto_now=True)
    emp = models.ForeignKey(Employee,on_delete=models.CASCADE)
    total = models.IntegerField(default=0)
    follow = models.IntegerField(default=0)
    Notanswer = models.IntegerField(default=0)
    Notinterested = models.IntegerField(default=0)

class TrashLead(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    lost = models.BooleanField(default= False)
