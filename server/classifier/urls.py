from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('emails/', views.EmailListView.as_view(), name='email_list'),
    path('emails/<int:pk>/', views.EmailDetailView.as_view(), name='email_detail'),
    path('about/', views.about, name='about'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/submit-email/', views.api_submit_email, name='api_submit_email'),
    path('api/emails/', views.api_emails_list, name='api_emails_list'),
    path('api/emails/<int:pk>/', views.api_email_detail, name='api_email_detail'),
    path('api/usage/', views.api_usage, name='api_usage'),
    path('api/jobs/<str:job_id>/', views.api_job_status, name='api_job_status'),
]
