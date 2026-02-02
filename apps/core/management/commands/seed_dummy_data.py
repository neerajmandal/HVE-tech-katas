from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import PatientProfile, Invoice, InvoiceLineItem
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seeds database with dummy hospital invoice data'

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
            # Check if user already exists
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

            # Create patient profile if it doesn't exist
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

        # Medical services with prices
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

        # Create 15 invoices - mostly unpaid
        invoice_count = Invoice.objects.count()
        starting_number = 2025001 + invoice_count

        for i in range(15):
            patient = random.choice(patients)

            # Most invoices are pending (unpaid), some are overdue, very few are paid
            status = random.choices(
                ['pending', 'overdue', 'paid'],
                weights=[70, 20, 10],  # 70% pending, 20% overdue, 10% paid
                k=1
            )[0]

            # Generate invoice number
            invoice_number = f'INV-{starting_number + i}'

            # Skip if invoice already exists
            if Invoice.objects.filter(invoice_number=invoice_number).exists():
                continue

            # Calculate due date
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

            # Add 1-4 line items per invoice
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

            # Update invoice totals (8% tax)
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

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully seeded dummy data!'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write('  Username: patient1 through patient20')
        self.stdout.write('  Password: password123')
