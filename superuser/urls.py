from django.urls import path
from .views import *

urlpatterns = [
    path("", dash, name="super_dash"),
    path("dashboard", dash, name="super_dash"),

    # Admin
    path("admin", admins, name="admin"),
    path("admin/<str:action>/", banned_admins, name="admin"),
    path("create_admin", create_admin, name="create_admin"),
    path("edit_admin<int:id>", edit_admin, name="edit_admin"),
    path("delete_admin<int:id>",delete_admin, name="delete_admin"),

    # Employee
    path("employee", employees, name="employee"),
    path("duty<int:id>", emp_duty, name="emp_duty"),
    path("admin_duty<int:id>", admin_duty, name="admin_duty"),
    path("employee/<str:action>/", banned_employee, name="employee"),
    path("delete_employee<int:id>",delete_employee, name="delete_employee"),
    # Leads
    path("lead", leads, name="super_lead"),
    path("campain_lead", campain_leads, name="super_campain_lead"),
    path("status<int:id>", status, name="super_status"),
    path("followup", follows, name="super_followups"),

    # Leads Won
    path("won", wons, name="won"),
    path("payment", payment, name="super_payment"),
    path("callback", callbacks, name="super_callback"),
    path("not_answered", naleads, name="super_naleads"),

    # Reports
    path("reports", reports_admin, name="super_reports"),
    path("reports<int:id>", report, name="view_reports"),
]