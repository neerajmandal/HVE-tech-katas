import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.core.models import (
    DoctorVisit,
    Invoice,
    InvoiceLineItem,
    LabTest,
    PatientProfile,
)

OPERATORS = [
    ("Marcus", "Reyes"),
    ("Tonya", "Okafor"),
    ("Diego", "Navarro"),
    ("Priya", "Sharma"),
    ("Liam", "O'Connor"),
    ("Yuki", "Tanaka"),
    ("Hannah", "Kowalski"),
    ("Omar", "Haddad"),
    ("Grace", "Mbeki"),
    ("Sven", "Larsson"),
    ("Carla", "Ferreira"),
    ("Wei", "Zhang"),
]

SITES = [
    ("Northgate Assembly Plant", "Mechanical"),
    ("Riverside Fabrication", "Electrical"),
    ("Westfield Distribution Center", "Controls"),
    ("Cedar Hill Stamping", "Mechanical"),
]

# Inspection readings -> LabTest. Discipline drives test_category.
INSPECTIONS = [
    {
        "test_name": "Vibration Analysis",
        "test_category": "Mechanical",
        "results": [
            ("RMS Velocity", "0.0-2.8", "mm/s"),
            ("Bearing Defect Freq", "0.0-1.5", "g"),
        ],
    },
    {
        "test_name": "Thermal Imaging",
        "test_category": "Electrical",
        "results": [
            ("Hotspot Delta", "0-15", "\u00b0C"),
            ("Connector Temp", "0-60", "\u00b0C"),
        ],
    },
    {
        "test_name": "Lubricant Analysis",
        "test_category": "Mechanical",
        "results": [
            ("Viscosity @40C", "28-34", "cSt"),
            ("Particle Count ISO", "0-18", "code"),
        ],
    },
    {
        "test_name": "Insulation Resistance",
        "test_category": "Electrical",
        "results": [
            ("Megger Reading", ">100", "M\u03a9"),
        ],
    },
    {
        "test_name": "Hydraulic Pressure Check",
        "test_category": "Controls",
        "results": [
            ("System Pressure", "180-210", "bar"),
        ],
    },
    {
        "test_name": "Alignment Survey",
        "test_category": "Mechanical",
        "results": [
            ("Angular Offset", "0.0-0.05", "mm/100mm"),
            ("Parallel Offset", "0.0-0.10", "mm"),
        ],
    },
    {
        "test_name": "Ultrasonic Thickness",
        "test_category": "Mechanical",
        "results": [
            ("Wall Thickness", "8.0-12.0", "mm"),
        ],
    },
    {
        "test_name": "PLC Signal Integrity",
        "test_category": "Controls",
        "results": [
            ("Loop Current", "4-20", "mA"),
        ],
    },
]

INSPECTORS = [
    "A. Reyes",
    "J. Castillo",
    "M. Lindqvist",
    "R. Patel",
    "T. Okafor",
]

# Work orders -> DoctorVisit. doctor_name=Technician, specialty=Discipline.
TECHNICIANS = [
    ("S. Whitfield", "Mechanical"),
    ("D. Navarro", "Electrical"),
    ("K. Brennan", "Controls"),
    ("P. Sharma", "Mechanical"),
    ("L. O'Connor", "Electrical"),
    ("G. Mbeki", "Controls"),
    ("W. Zhang", "Mechanical"),
]

# (work requested, visit_type)
WORK_ORDERS = [
    ("Scheduled routine inspection of conveyor drive", "checkup"),
    ("Re-inspection after bearing replacement", "follow_up"),
    ("Line 3 conveyor stopped - unplanned breakdown", "urgent"),
    ("Specialist vibration root-cause investigation", "specialist"),
    ("Quarterly preventive maintenance on hydraulic press", "preventive"),
    ("Gearbox overheating reported by line lead", "urgent"),
    ("Follow-up alignment verification on pump skid", "follow_up"),
    ("Annual safety relief valve service", "preventive"),
    ("PLC fault diagnosis on packaging cell", "specialist"),
    ("Routine lubrication round - Zone A", "checkup"),
]

FINDINGS = [
    "Bearing wear within limits; continue monitoring.",
    "Coupling misalignment detected; corrected on site.",
    "Lubricant degraded beyond service interval.",
    "Loose terminal connection causing intermittent fault.",
    "Hydraulic seal leak at cylinder rod end.",
    "No defects found; equipment operating in spec.",
    "Belt tension below specification.",
    "Motor insulation resistance trending downward.",
    "Sensor drift outside calibration tolerance.",
    "Excessive vibration traced to unbalanced fan.",
]

CORRECTIVE_ACTIONS = [
    "Replace bearing at next planned shutdown. Re-inspect in 30 days.",
    "Re-align coupling and record laser report. Monitor weekly.",
    "Drain and replace lubricant. Sample again in 90 days.",
    "Torque terminals to spec and thermal-scan after 1 week.",
    "Replace rod seal kit. Pressure-test before return to service.",
    "No action required. Resume normal PM schedule.",
    "Adjust belt tension and log. Verify on next round.",
    "Schedule motor rewind. Trend insulation monthly.",
    "Recalibrate sensor and update calibration register.",
    "Balance fan assembly and re-measure vibration.",
]

# Purchase order parts -> InvoiceLineItem.
PARTS = [
    ("SKF Spherical Roller Bearing 22216", Decimal("420.00")),
    ("Hydraulic Cylinder Seal Kit", Decimal("85.50")),
    ("Allen-Bradley PLC Input Module", Decimal("615.00")),
    ("V-Belt Set B-Section (x3)", Decimal("64.00")),
    ("Synthetic Gear Oil ISO 320 (20L)", Decimal("198.75")),
    ("Vibration Sensor Accelerometer", Decimal("310.00")),
    ("Pneumatic Solenoid Valve 24VDC", Decimal("142.30")),
    ("Stainless Coupling Element", Decimal("76.40")),
    ("Thermal Overload Relay", Decimal("119.90")),
    ("Lubrication Grease Cartridge (case)", Decimal("88.00")),
]

SUPPLIERS = [
    "Apex Industrial Supply",
    "Northern Bearing Co.",
    "Voltvision Electric",
    "Summit MRO Distributors",
    "Precision Fluid Power",
]


class Command(BaseCommand):
    help = "Seeds database with synthetic manufacturing (plant operations) data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Resetting demo data..."))

        # Delete in FK-safe order, then the demo operator logins.
        InvoiceLineItem.objects.all().delete()
        Invoice.objects.all().delete()
        DoctorVisit.objects.all().delete()
        LabTest.objects.all().delete()
        PatientProfile.objects.all().delete()
        User.objects.filter(username__startswith="operator").delete()

        self.stdout.write(self.style.WARNING("Seeding operators..."))

        operators = []
        for i, (first_name, last_name) in enumerate(OPERATORS, 1):
            username = f"operator{i}"
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="password123",  # pragma: allowlist secret
                first_name=first_name,
                last_name=last_name,
            )

            site_name, discipline = SITES[i % len(SITES)]
            PatientProfile.objects.create(
                user=user,
                date_of_birth=datetime(1975 + (i % 25), (i % 12) + 1, 12).date(),
                phone_number=f"555-{2000 + i:04d}",
                address=f"{site_name}, Bay {i % 8 + 1}, Industrial Park, ST 24680",
                insurance_provider=site_name,
                insurance_policy_number=f"BADGE-{4000 + i}",
            )

            operators.append(user)
            self.stdout.write(self.style.SUCCESS(f"Created operator: {username}"))

        # --- Seed Inspection readings (LabTest) ---
        self.stdout.write(self.style.WARNING("\nSeeding inspections..."))

        for operator in operators:
            num_inspections = random.randint(3, 6)
            selected = random.sample(
                INSPECTIONS, min(num_inspections, len(INSPECTIONS))
            )

            for inspection in selected:
                status = random.choices(
                    ["completed", "reviewed", "pending"], weights=[50, 30, 20], k=1
                )[0]

                order_date = datetime.now().date() - timedelta(
                    days=random.randint(1, 180)
                )
                result_date = (
                    order_date + timedelta(days=random.randint(1, 5))
                    if status != "pending"
                    else None
                )

                metric_name, ref_range, unit = random.choice(inspection["results"])
                out_of_spec = random.random() < 0.15

                if ref_range.startswith("<"):
                    base = float(ref_range[1:])
                    value = base * 1.3 if out_of_spec else base * 0.7
                elif ref_range.startswith(">"):
                    base = float(ref_range[1:])
                    value = base * 0.7 if out_of_spec else base * 1.3
                elif "-" in ref_range:
                    low, high = (float(p) for p in ref_range.split("-"))
                    value = high * 1.25 if out_of_spec else random.uniform(low, high)
                else:
                    value = 0
                    out_of_spec = False

                result_value = f"{value:.2f}" if status != "pending" else ""

                LabTest.objects.create(
                    patient=operator,
                    test_name=f"{inspection['test_name']} - {metric_name}",
                    test_category=inspection["test_category"],
                    ordered_by=random.choice(INSPECTORS),
                    order_date=order_date,
                    result_date=result_date,
                    status=status,
                    result_value=result_value,
                    reference_range=ref_range,
                    unit=unit,
                    is_abnormal=out_of_spec if status != "pending" else False,
                    notes="Out of spec - corrective work order raised."
                    if out_of_spec and status != "pending"
                    else "",
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created inspections for {operator.get_full_name()}"
                )
            )

        # --- Seed Work Orders (DoctorVisit) ---
        self.stdout.write(self.style.WARNING("\nSeeding work orders..."))

        for operator in operators:
            num_orders = random.randint(2, 5)

            for _ in range(num_orders):
                technician, discipline = random.choice(TECHNICIANS)
                work_requested, visit_type = random.choice(WORK_ORDERS)
                visit_date = datetime.now().date() - timedelta(
                    days=random.randint(7, 365)
                )
                follow_up = (
                    visit_date + timedelta(days=random.randint(30, 90))
                    if random.random() > 0.4
                    else None
                )

                DoctorVisit.objects.create(
                    patient=operator,
                    doctor_name=technician,
                    specialty=discipline,
                    visit_date=visit_date,
                    visit_type=visit_type,
                    reason=work_requested,
                    diagnosis=random.choice(FINDINGS),
                    treatment_plan=random.choice(CORRECTIVE_ACTIONS),
                    follow_up_date=follow_up,
                    notes="",
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created work orders for {operator.get_full_name()}"
                )
            )

        # --- Seed Purchase Orders (Invoice) ---
        self.stdout.write(self.style.WARNING("\nSeeding purchase orders..."))

        starting_number = 2025001

        for i in range(15):
            operator = random.choice(operators)
            status = random.choices(
                ["pending", "overdue", "paid"], weights=[60, 25, 15], k=1
            )[0]
            po_number = f"PO-{starting_number + i}"

            if status == "overdue":
                due_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
            else:
                due_date = datetime.now().date() + timedelta(
                    days=random.randint(15, 45)
                )

            invoice = Invoice.objects.create(
                invoice_number=po_number,
                patient=operator,
                due_date=due_date,
                status=status,
                subtotal=Decimal("0.00"),
                tax=Decimal("0.00"),
                total=Decimal("0.00"),
                notes="Net 30. Confirm receipt against work order."
                if status == "pending"
                else "",
            )

            subtotal = Decimal("0.00")
            num_items = random.randint(1, 4)

            for _ in range(num_items):
                part_name, unit_price = random.choice(PARTS)
                quantity = random.randint(1, 4)
                total_price = unit_price * quantity

                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=part_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    service_date=datetime.now().date()
                    - timedelta(days=random.randint(1, 30)),
                    provider_name=random.choice(SUPPLIERS),
                )
                subtotal += total_price

            tax = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
            total = subtotal + tax

            invoice.subtotal = subtotal
            invoice.tax = tax
            invoice.total = total
            invoice.save()

            status_color = {
                "pending": self.style.WARNING,
                "overdue": self.style.ERROR,
                "paid": self.style.SUCCESS,
            }[status]

            self.stdout.write(
                status_color(
                    f"Created purchase order {po_number} for "
                    f"{operator.get_full_name()} - ${total} [{status.upper()}]"
                )
            )

        self.stdout.write(
            self.style.SUCCESS("\nSuccessfully seeded manufacturing data!")
        )
        self.stdout.write(self.style.SUCCESS("Login credentials:"))
        self.stdout.write("  Username: operator1 through operator12")
        self.stdout.write("  Password: password123")
