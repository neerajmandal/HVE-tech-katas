from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('free-tools/', views.free_tools, name='free_tools'),
    path('free-tools/investment-calculator/', views.investment_calculator, name='investment_calculator'),
    path('welcome/', views.welcome, name='welcome'),
    path('invoices/', views.invoice_list, name='invoice_list'),
]