from django.db import models
from django.contrib.auth.models import User


class PatientProfile(models.Model):
    """Extended patient information linked to User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email}"


class LabTest(models.Model):
    """Lab test results for a patient"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_tests')
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=100)
    ordered_by = models.CharField(max_length=100)
    order_date = models.DateField()
    result_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_value = models.CharField(max_length=100, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    is_abnormal = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"{self.test_name} - {self.patient.get_full_name()} ({self.status})"


class DoctorVisit(models.Model):
    """Record of a patient's doctor visit"""
    VISIT_TYPE_CHOICES = [
        ('checkup', 'Annual Checkup'),
        ('follow_up', 'Follow-up'),
        ('urgent', 'Urgent Care'),
        ('specialist', 'Specialist Referral'),
        ('preventive', 'Preventive Care'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_visits')
    doctor_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    visit_date = models.DateField()
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='checkup')
    reason = models.CharField(max_length=300)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    vitals_bp = models.CharField(max_length=20, blank=True)
    vitals_heart_rate = models.IntegerField(null=True, blank=True)
    vitals_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    vitals_weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.doctor_name} - {self.patient.get_full_name()} ({self.visit_date})"


class Invoice(models.Model):
    """Medical invoice for patient services"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.patient.get_full_name()} - ${self.total}"


class InvoiceLineItem(models.Model):
    """Individual service/charge on an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    service_date = models.DateField()
    provider_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.description} - ${self.total_price}"
