from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import PatientProfile, Invoice, InvoiceLineItem, LabTest, DoctorVisit
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seeds database with dummy healthcare portal data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding database with dummy data...'))

        # Create 20 dummy patients
        patients = []
        patient_names = [
            ('John', 'Smith'),
            ('Sarah', 'Johnson'),
            ('Michael', 'Williams'),
            ('Emily', 'Brown'),
            ('David', 'Martinez'),
            ('Jessica', 'Garcia'),
            ('Robert', 'Rodriguez'),
            ('Ashley', 'Davis'),
            ('James', 'Wilson'),
            ('Amanda', 'Moore'),
            ('Christopher', 'Taylor'),
            ('Jennifer', 'Anderson'),
            ('Daniel', 'Thomas'),
            ('Lisa', 'Jackson'),
            ('Matthew', 'White'),
            ('Karen', 'Harris'),
            ('Joshua', 'Martin'),
            ('Nancy', 'Thompson'),
            ('Andrew', 'Lee'),
            ('Betty', 'Clark'),
        ]

        for i, (first_name, last_name) in enumerate(patient_names, 1):
            username = f'patient{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

            profile, created = PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    'date_of_birth': datetime(1970 + (i % 30), (i % 12) + 1, 15).date(),
                    'phone_number': f'555-{1000+i:04d}',
                    'address': f'{i}00 Medical Plaza Dr, Suite {i*10}, City, ST 12345',
                    'insurance_provider': 'BlueCross' if i % 2 == 0 else 'Aetna',
                    'insurance_policy_number': f'POL-{1000+i}',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created patient profile for {first_name} {last_name}'))

            patients.append(user)

        # --- Seed Lab Tests ---
        self.stdout.write(self.style.WARNING('\nSeeding lab tests...'))

        lab_tests_data = [
            {
                'test_name': 'Complete Blood Count (CBC)',
                'test_category': 'Hematology',
                'results': [
                    ('WBC', '4.5-11.0', '10^3/uL'),
                    ('RBC', '4.7-6.1', '10^6/uL'),
                    ('Hemoglobin', '14.0-18.0', 'g/dL'),
                ],
            },
            {
                'test_name': 'Basic Metabolic Panel (BMP)',
                'test_category': 'Chemistry',
                'results': [
                    ('Glucose', '70-100', 'mg/dL'),
                    ('Calcium', '8.5-10.5', 'mg/dL'),
                    ('Sodium', '136-145', 'mEq/L'),
                ],
            },
            {
                'test_name': 'Lipid Panel',
                'test_category': 'Chemistry',
                'results': [
                    ('Total Cholesterol', '<200', 'mg/dL'),
                    ('HDL', '>40', 'mg/dL'),
                    ('LDL', '<100', 'mg/dL'),
                    ('Triglycerides', '<150', 'mg/dL'),
                ],
            },
            {
                'test_name': 'Thyroid Stimulating Hormone (TSH)',
                'test_category': 'Endocrinology',
                'results': [
                    ('TSH', '0.4-4.0', 'mIU/L'),
                ],
            },
            {
                'test_name': 'Hemoglobin A1C',
                'test_category': 'Chemistry',
                'results': [
                    ('HbA1c', '<5.7', '%'),
                ],
            },
            {
                'test_name': 'Urinalysis',
                'test_category': 'Urinalysis',
                'results': [
                    ('pH', '4.5-8.0', ''),
                    ('Specific Gravity', '1.005-1.030', ''),
                ],
            },
            {
                'test_name': 'Liver Function Panel',
                'test_category': 'Chemistry',
                'results': [
                    ('ALT', '7-56', 'U/L'),
                    ('AST', '10-40', 'U/L'),
                    ('Albumin', '3.5-5.0', 'g/dL'),
                ],
            },
            {
                'test_name': 'Vitamin D, 25-Hydroxy',
                'test_category': 'Chemistry',
                'results': [
                    ('Vitamin D', '30-100', 'ng/mL'),
                ],
            },
        ]

        doctors = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Martinez']

        for patient in patients:
            if LabTest.objects.filter(patient=patient).exists():
                continue

            num_tests = random.randint(3, 6)
            selected_tests = random.sample(lab_tests_data, min(num_tests, len(lab_tests_data)))

            for test_data in selected_tests:
                status = random.choices(
                    ['completed', 'reviewed', 'pending'],
                    weights=[50, 30, 20],
                    k=1
                )[0]

                order_date = datetime.now().date() - timedelta(days=random.randint(1, 180))
                result_date = order_date + timedelta(days=random.randint(1, 5)) if status != 'pending' else None

                result_info = random.choice(test_data['results'])
                ref_range = result_info[1]
                unit = result_info[2]

                is_abnormal = random.random() < 0.15
                if ref_range.startswith('<'):
                    normal_val = float(ref_range[1:]) * 0.7
                    result_val = float(ref_range[1:]) * 1.3 if is_abnormal else normal_val
                elif ref_range.startswith('>'):
                    normal_val = float(ref_range[1:]) * 1.3
                    result_val = float(ref_range[1:]) * 0.7 if is_abnormal else normal_val
                elif '-' in ref_range:
                    parts = ref_range.split('-')
                    low, high = float(parts[0]), float(parts[1])
                    normal_val = random.uniform(low, high)
                    result_val = high * 1.2 if is_abnormal else normal_val
                else:
                    result_val = 0
                    is_abnormal = False

                result_value = f"{result_val:.1f}" if status != 'pending' else ''

                LabTest.objects.create(
                    patient=patient,
                    test_name=test_data['test_name'],
                    test_category=test_data['test_category'],
                    ordered_by=random.choice(doctors),
                    order_date=order_date,
                    result_date=result_date,
                    status=status,
                    result_value=result_value,
                    reference_range=ref_range,
                    unit=unit,
                    is_abnormal=is_abnormal if status != 'pending' else False,
                    notes='Abnormal result - follow up recommended.' if is_abnormal and status != 'pending' else '',
                )

            self.stdout.write(self.style.SUCCESS(
                f'Created {num_tests} lab tests for {patient.get_full_name()}'
            ))

        # --- Seed Doctor Visits ---
        self.stdout.write(self.style.WARNING('\nSeeding doctor visits...'))

        specialties = [
            ('Dr. Smith', 'Internal Medicine'),
            ('Dr. Johnson', 'Family Medicine'),
            ('Dr. Williams', 'Cardiology'),
            ('Dr. Brown', 'Endocrinology'),
            ('Dr. Martinez', 'Pulmonology'),
            ('Dr. Garcia', 'Orthopedics'),
            ('Dr. Wilson', 'Dermatology'),
        ]

        visit_reasons = [
            ('Annual physical examination', 'checkup'),
            ('Follow-up on blood pressure management', 'follow_up'),
            ('Persistent cough and congestion', 'urgent'),
            ('Referral for cardiac evaluation', 'specialist'),
            ('Flu vaccination and wellness check', 'preventive'),
            ('Knee pain and stiffness', 'specialist'),
            ('Diabetes management review', 'follow_up'),
            ('Skin rash evaluation', 'urgent'),
            ('Cholesterol level follow-up', 'follow_up'),
            ('Routine preventive screening', 'preventive'),
        ]

        diagnoses = [
            'Hypertension, well-controlled with current medication.',
            'Type 2 Diabetes Mellitus - stable, continue current treatment plan.',
            'Upper respiratory infection - viral, self-limiting.',
            'Hyperlipidemia - recommend dietary modifications.',
            'Osteoarthritis of the knee - mild.',
            'No acute findings. Continue preventive care.',
            'Vitamin D deficiency - supplementation recommended.',
            'Seasonal allergies - prescribed antihistamine.',
            'Anxiety disorder - referral to behavioral health.',
            'Pre-diabetes - lifestyle modification counseling provided.',
        ]

        treatment_plans = [
            'Continue current medications. Recheck in 3 months.',
            'Increase exercise to 30 min/day. Follow up in 6 weeks.',
            'Rest, fluids, OTC symptom relief. Return if worsening.',
            'Start statin therapy. Recheck lipid panel in 3 months.',
            'Physical therapy 2x/week for 6 weeks. Ice and elevation.',
            'Annual labs ordered. Return for results review.',
            'Vitamin D 2000 IU daily. Recheck in 3 months.',
            'Antihistamine as needed. Avoid known triggers.',
            'Referral placed. Consider therapy and/or medication.',
            'Dietary counseling. HbA1c recheck in 3 months.',
        ]

        for patient in patients:
            if DoctorVisit.objects.filter(patient=patient).exists():
                continue

            num_visits = random.randint(2, 5)

            for _ in range(num_visits):
                doctor, specialty = random.choice(specialties)
                reason_text, visit_type = random.choice(visit_reasons)
                visit_date = datetime.now().date() - timedelta(days=random.randint(7, 365))
                follow_up = visit_date + timedelta(days=random.randint(30, 90)) if random.random() > 0.3 else None

                DoctorVisit.objects.create(
                    patient=patient,
                    doctor_name=doctor,
                    specialty=specialty,
                    visit_date=visit_date,
                    visit_type=visit_type,
                    reason=reason_text,
                    diagnosis=random.choice(diagnoses),
                    treatment_plan=random.choice(treatment_plans),
                    follow_up_date=follow_up,
                    vitals_bp=f'{random.randint(110, 140)}/{random.randint(65, 90)}',
                    vitals_heart_rate=random.randint(60, 100),
                    vitals_temperature=Decimal(str(round(random.uniform(97.0, 99.5), 1))),
                    vitals_weight=Decimal(str(round(random.uniform(120, 250), 1))),
                    notes='',
                )

            self.stdout.write(self.style.SUCCESS(
                f'Created {num_visits} doctor visits for {patient.get_full_name()}'
            ))

        # --- Seed Invoices ---
        self.stdout.write(self.style.WARNING('\nSeeding invoices...'))

        services = [
            ('General Checkup', Decimal('150.00')),
            ('X-Ray - Chest', Decimal('250.00')),
            ('Blood Test - CBC', Decimal('75.00')),
            ('MRI Scan', Decimal('1200.00')),
            ('Physical Therapy Session', Decimal('120.00')),
            ('Vaccination - Flu Shot', Decimal('35.00')),
            ('Emergency Room Visit', Decimal('500.00')),
            ('Cardiology Consultation', Decimal('200.00')),
            ('Orthopedic Consultation', Decimal('180.00')),
            ('Lab Work - Metabolic Panel', Decimal('95.00')),
        ]

        providers = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Martinez']

        invoice_count = Invoice.objects.count()
        starting_number = 2025001 + invoice_count

        for i in range(15):
            patient = random.choice(patients)
            status = random.choices(
                ['pending', 'overdue', 'paid'],
                weights=[70, 20, 10],
                k=1
            )[0]
            invoice_number = f'INV-{starting_number + i}'
            if Invoice.objects.filter(invoice_number=invoice_number).exists():
                continue

            if status == 'overdue':
                due_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
            else:
                due_date = datetime.now().date() + timedelta(days=random.randint(15, 45))

            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                patient=patient,
                due_date=due_date,
                status=status,
                subtotal=Decimal('0.00'),
                tax=Decimal('0.00'),
                total=Decimal('0.00'),
                notes='Please pay by due date to avoid late fees.' if status == 'pending' else ''
            )

            subtotal = Decimal('0.00')
            num_items = random.randint(1, 4)

            for _ in range(num_items):
                service = random.choice(services)
                quantity = random.randint(1, 2)
                unit_price = service[1]
                total_price = unit_price * quantity

                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=service[0],
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    service_date=datetime.now().date() - timedelta(days=random.randint(1, 30)),
                    provider_name=random.choice(providers)
                )
                subtotal += total_price

            tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
            total = subtotal + tax

            invoice.subtotal = subtotal
            invoice.tax = tax
            invoice.total = total
            invoice.save()

            status_color = {
                'pending': self.style.WARNING,
                'overdue': self.style.ERROR,
                'paid': self.style.SUCCESS
            }[status]

            self.stdout.write(status_color(
                f'Created invoice {invoice_number} for {patient.get_full_name()} - '
                f'${total} [{status.upper()}]'
            ))

        self.stdout.write(self.style.SUCCESS('\nSuccessfully seeded dummy data!'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write('  Username: patient1 through patient20')
        self.stdout.write('  Password: password123')
