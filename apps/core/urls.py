from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('free-tools/', views.free_tools, name='free_tools'),
    path('free-tools/investment-calculator/', views.investment_calculator, name='investment_calculator'),
    path('welcome/', views.welcome, name='welcome'),
    path('portal/', views.patient_dashboard, name='patient_dashboard'),
    path('portal/lab-tests/', views.lab_tests, name='lab_tests'),
    path('portal/visits/', views.doctor_visits, name='doctor_visits'),
    path('invoices/', views.invoice_list, name='invoice_list'),
]
