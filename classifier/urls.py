from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('emails/', views.EmailListView.as_view(), name='email_list'),
    path('emails/<int:pk>/', views.EmailDetailView.as_view(), name='email_detail'),
    path('about/', views.about, name='about'),
]
