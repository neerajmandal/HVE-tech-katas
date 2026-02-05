from django.contrib import admin
from .models import PatientProfile, Invoice, InvoiceLineItem, LabTest, DoctorVisit


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'total_price', 'service_date', 'provider_name']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'insurance_provider', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number']
    list_filter = ['insurance_provider', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'patient', 'test_category', 'status', 'order_date', 'is_abnormal']
    list_filter = ['status', 'test_category', 'is_abnormal', 'order_date']
    search_fields = ['test_name', 'patient__username', 'patient__first_name', 'patient__last_name', 'ordered_by']


@admin.register(DoctorVisit)
class DoctorVisitAdmin(admin.ModelAdmin):
    list_display = ['doctor_name', 'patient', 'specialty', 'visit_type', 'visit_date']
    list_filter = ['visit_type', 'specialty', 'visit_date']
    search_fields = ['doctor_name', 'patient__username', 'patient__first_name', 'patient__last_name', 'reason']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'total', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'patient__username', 'patient__email', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceLineItemInline]
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient', 'status', 'due_date', 'notes')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax', 'total')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'total_price', 'service_date']
    list_filter = ['service_date', 'provider_name']
    search_fields = ['description', 'invoice__invoice_number', 'provider_name']
