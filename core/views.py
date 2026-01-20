from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, AppointmentForm, GalleryImageForm
from .models import User, Appointment, GalleryImage
from .decorators import role_required

from django.db.models import Avg, Count


def home(request):
    doctors = User.objects.filter(role='DOCTOR').annotate(
        avg_rating=Avg('doctor_ratings__stars'),
        total_reviews=Count('doctor_ratings')
    )
    return render(request, "home.html", {"doctors": doctors})


def about(request):
    return render(request, 'about.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == User.PATIENT:
                messages.success(request, 'Registration successful. You are logged in as patient.')
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, 'Registration received. Admin approval required before you can login.')
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def dashboard(request):
    user = request.user
    context = {}
    if user.role == User.PATIENT:
        context['my_appointments'] = Appointment.objects.filter(patient=user)
    
    elif user.role == User.DOCTOR:
        assigned_qs = Appointment.objects.filter(doctor=user).order_by('-date', '-time')

        # NEW NOTIFICATION LOGIC
        new_qs = assigned_qs.filter(is_seen_by_doctor=False)

        context['assigned'] = assigned_qs
        context['new_appointments'] = new_qs
        context['new_count'] = new_qs.count()

        # Mark notifications as seen after viewing dashboard
        if new_qs.exists():
            new_qs.update(is_seen_by_doctor=True)

    elif user.role == User.STAFF:
        context['all_appointments'] = Appointment.objects.select_related('patient', 'doctor').all()
    return render(request, 'dashboard.html', context)


@login_required
@role_required(User.PATIENT)
def book_appointment(request):  # MAIN FUNCTION (UPDATED)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)

            appointment.patient = request.user
            appointment.status = 'Pending Payment'

            # ⭐ NEW FIELDS ADDED HERE
            appointment.patient_name = request.POST.get("patient_name")
            appointment.contact_number = request.POST.get("contact_number")

            appointment.save()

            # ⭐⭐⭐ EMAIL NOTIFICATION TO DOCTOR ⭐⭐⭐
            from django.core.mail import send_mail
            from django.conf import settings

            subject = "New Appointment Booked"
            message = (
                f"Dear Dr. {appointment.doctor.get_full_name() or appointment.doctor.username},\n\n"
                f"You have a new appointment.\n\n"
                f"Patient Name: {appointment.patient_name}\n"
                f"Contact Number: {appointment.contact_number}\n"
                f"Date: {appointment.date}\n"
                f"Time: {appointment.time}\n"
                f"Symptoms: {appointment.symptoms or 'Not provided'}\n\n"
                f"Please login to your dashboard for details."
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [appointment.doctor.email],
                    fail_silently=True,   # No error even if email fails
                )
            except:
                pass

            return redirect('appointment_payment', pk=appointment.pk)

    else:
        form = AppointmentForm()

    return render(request, 'appointment_book.html', {'form': form})

@login_required
def gallery(request):
    images = GalleryImage.objects.all()
    upload_form = None
    if request.user.role in (User.DOCTOR, User.STAFF):
        if request.method == 'POST':
            upload_form = GalleryImageForm(request.POST, request.FILES)
            if upload_form.is_valid():
                g = upload_form.save(commit=False)
                g.uploader = request.user
                g.save()
                messages.success(request, 'Image uploaded to gallery.')
                return redirect('gallery')
        else:
            upload_form = GalleryImageForm()
    return render(request, 'gallery.html', {'images': images, 'upload_form': upload_form})


@login_required
@role_required(User.DOCTOR)
def update_appointment_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appt.status = new_status
            appt.save()
            messages.success(request, 'Status updated.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('dashboard')


@login_required
@role_required(User.PATIENT)
def appointment_payment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "UPI")

        appt.status = "PENDING"
        appt.payment_status = "SUCCESS"
        appt.payment_method = payment_method
        appt.save()

        messages.success(request, "💳 Payment successful! Appointment confirmed.")
        return redirect("dashboard")

    return render(request, "payment.html", {"appointment": appt})


@login_required
@role_required(User.PATIENT)
def confirm_payment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    appt.status = 'CONFIRMED'
    appt.save()
    messages.success(request, "Payment successful! Appointment confirmed.")
    return redirect('dashboard')


from .models import Rating, User
from django.contrib.auth.decorators import login_required


@login_required
def rate_doctor(request, doctor_id):
    doctor = User.objects.get(id=doctor_id, role='DOCTOR')

    if request.user.role != "PATIENT":
        messages.error(request, "Only Patients can submit ratings.")
        return redirect("home")

    existing = Rating.objects.filter(doctor=doctor, patient=request.user).first()

    if request.method == "POST":
        stars = int(request.POST.get("stars", 5))
        review = request.POST.get("review", "")

        if existing:
            existing.stars = stars
            existing.review = review
            existing.save()
            messages.success(request, "Your rating has been updated.")
        else:
            Rating.objects.create(
                doctor=doctor,
                patient=request.user,
                stars=stars,
                review=review
            )
            messages.success(request, "Thank you! Your rating has been submitted.")

        return redirect("home")

    return render(request, "rate_doctor.html", {
        "doctor": doctor,
        "existing": existing
    })

