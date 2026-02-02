from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('billing/portal/', views.customer_portal, name='customer_portal'),
]