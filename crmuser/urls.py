from django.urls import path
from.import views


urlpatterns = [
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('lead', views.lead,name='user_lead'),
    path('campain_lead', views.campain_lead,name='user_campain_lead'),
    path('campain_follow', views.campain_followups, name='campain_follow)'),
    path('quality_follow', views.quality_followups, name='quality_follow)'),
    path('status_<int:id>', views.status,name='status'),
    # path('<int:id>', views.del_payment, name='del_payment'),
    path('follow-ups', views.followups, name='followups)'),
    path('total_follow', views.totalfollow, name='totalfollow)'),
    path('won', views.leads_won, name='leads_won)'),
    path('callbacks', views.callbacks, name='callbacks)'),
    path('syllabus', views.syllabus, name='syllabus)'),
    path('user_reports', views.salereports, name='user_reports'),
]
