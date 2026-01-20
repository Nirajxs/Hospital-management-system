from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    PATIENT = 'PATIENT'
    DOCTOR = 'DOCTOR'
    STAFF = 'STAFF'

    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
        (STAFF, 'Staff'),
    ] 

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)

    # ⭐⭐ Doctor extra fields — SAFELY ADDED ⭐⭐
    speciality = models.CharField(max_length=100, null=True, blank=True)
    work_from = models.CharField(max_length=150, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    qualification = models.CharField(max_length=150, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"  # type: ignore


class Appointment(models.Model): 
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_made')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_received', limit_choices_to={'role': 'DOCTOR'})
    date = models.DateField()
    time = models.TimeField()
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    
    
    # inside class Appointment(models.Model):
    ...
    # NEW: mark whether doctor has seen this appointment notification
    is_seen_by_doctor = models.BooleanField(default=False)
    ...


    symptoms = models.TextField(blank=True)
    image = models.ImageField(upload_to='appointments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Appt #{self.id} - {self.patient} -> {self.doctor} on {self.date} {self.time}" #type: ignore


class GalleryImage(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Image #{self.id} by {self.uploader}" #type: ignore





# NOTE: This view SHOULD be in views.py (not models.py)
# I am NOT modifying logic.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
# from .models import Appointment   # ❌ Already imported above, so commented to prevent circular import


def appointment_payment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        method = request.POST.get("payment_method")

        if not method:
            messages.error(request, "Please select a payment method.")
            return redirect("appointment_payment", pk=appointment.pk)

        appointment.payment_method = method.upper()
        appointment.payment_status = "SUCCESS"
        appointment.status = "PENDING"
        appointment.save()

        messages.success(request, f"Payment successful using {method.title()}! Appointment confirmed.")
        return redirect("dashboard")

    return render(request, "payment.html", {"appointment": appointment})



class Rating(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_ratings",
                               limit_choices_to={'role': 'DOCTOR'})
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_ratings",
                                limit_choices_to={'role': 'PATIENT'})
    stars = models.IntegerField(default=5)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'patient')  # Patient ek baar hi rate karega doctor ko

    def __str__(self):
        return f"{self.doctor.username} rated {self.stars}"

