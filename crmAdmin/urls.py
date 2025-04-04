from django.urls import path
from crmAdmin import views

urlpatterns=[
       # Meta Connection
       # path("meta/leads", views.facebook_webhook,name="facebook-webhook"),
       path("privacy_policy", views.privacy,name="privacy-policy"),

       # Dashboard
       path('',views.dash,name="dash"),
       path('dashboard',views.dash,name="dash"),
       
       # Lead
       path('lead', views.leads, name="lead"),
       path('campain_leads', views.campain_leads, name="campain_leads"),
       path('edit_lead/<int:id>', views.edit_lead, name="edit_lead"),
       path('del_lead/<int:id>',views.del_lead,name="del_lead"),
       path('lead/<int:id>/status', views.lead_status, name="lead_status"),
       
       # Employees
       path('employee',views.employee,name='admin_employee'),
       path('blocked_emp',views.blocked_emp,name='blocked_emp'),
       path('daily',views.daily,name='daily'),
       path('monthly',views.monthly,name='monthly'),
       path('edit_emp/<int:id>', views.edit_emp, name="edit_emp"),
       path('del_emp/<int:id>', views.del_emp, name="del_emp"),

       # Duty
       path('duty/<int:id>', views.duty, name='duty'),
       path('del_duty/<int:id>', views.del_duty, name='del_duty'),
       path('assign_duties', views.assign, name="assign"), 
       path('assign_lead/<int:id>', views.assign_lead, name="assign_lead"),
       path('assign_all_lead/', views.assign_all_lead, name="assign_all"),
       
       # Courses
       path('course', views.courses, name='course'),
       path('edit-course/<int:id>', views.edit_course, name='edit_course'),
       path('delete-course/<int:id>', views.del_course, name='del_course'),

       # Followups
       path('followup', views.followup, name='followup'),

       # Not Answered Leads
       path('not_answered', views.not_answered, name='not_answered'),

       # Trash
       path('trash', views.trash_leads, name='trash'),
       path('recovery<int:id>', views.recover_lead, name='recovery'),

       # Payments
       path('payment',views.payments,name="payments"),
       
       # Callbacks
       path('callbacks',views.callbacks,name="callbacks"),
       
       # Won
       path('leads_won', views.won, name="won"),
       
       # Reports
       path('reports', views.reports, name='reports'),

       # Settings
       path('settings', views.settings, name='settings'),
       path('delete-user/<int:id>', views.del_suser, name='del_suser'),
]