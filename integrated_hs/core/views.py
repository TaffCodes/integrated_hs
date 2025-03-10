import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PatientRegistrationForm, PatientLoginForm, DoctorLoginForm, NurseLoginForm, ReceptionistLoginForm, AppointmentForm, DoctorAvailabilityForm, DoctorDashboardForm, DiagnosisForm
from .models import Patient, Doctor, Nurse, Receptionist, Appointment, TimeSlot, Diagnosis, Invoice, Prescription, Insight
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils.timezone import is_naive, make_naive
from .predict import generate_insights

# Add this utility function at the top of your views.py file or in a utils.py file
def get_filtered_available_timeslots(doctor_id):
    """
    Utility function to get available time slots for a doctor,
    filtering out booked slots and slots in the past.
    """
    # Current date and time for filtering
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    
    # Get all booked datetime combinations for this doctor
    booked_datetimes = Appointment.objects.filter(
        doctor_id=doctor_id
    ).values_list('date', flat=True)
    
    # Convert datetime objects to strings for easier comparison
    booked_datetime_strings = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in booked_datetimes]
    
    # Get all time slots for this doctor (not in the past)
    available_slots = TimeSlot.objects.filter(
        doctor_id=doctor_id,
        date__gte=current_date
    ).order_by('date', 'start_time')
    
    # Filter out slots that are already booked or in the past
    available_slots_filtered = []
    
    for slot in available_slots:
        # Create datetime object for this slot
        slot_datetime = datetime.combine(slot.date, slot.start_time)
        
        # Skip slots in the past (if same day, check time too)
        if slot.date == current_date and slot.start_time <= current_datetime.time():
            continue
            
        # Check if this slot is already booked
        slot_datetime_str = slot_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        if slot_datetime_str not in booked_datetime_strings:
            available_slots_filtered.append(slot.id)
    
    return TimeSlot.objects.filter(id__in=available_slots_filtered)



logger = logging.getLogger(__name__)

def hello(request):
    return render(request, './hello.html')

def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, './patient_register.html', {'form': form})

def patient_login(request):
    if request.method == 'POST':
        form = PatientLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    patient = Patient.objects.get(user=user)
                    login(request, user)
                    return redirect('patient_dashboard')
                except Patient.DoesNotExist:
                    logger.error("User %s is not a patient", username)
                    form.add_error(None, "Invalid username or password")
            else:
                logger.error("Authentication failed for user: %s", username)
                form.add_error(None, "Invalid username or password")
        else:
            logger.error("Form is not valid: %s", form.errors)
    else:
        form = PatientLoginForm()
    return render(request, './patient_login.html', {'form': form})

def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    doctor = Doctor.objects.get(user=user)
                    login(request, user)
                    return redirect('doctor_dashboard')
                except Doctor.DoesNotExist:
                    logger.error("User %s is not a doctor", username)
                    form.add_error(None, "Invalid username or password")
            else:
                logger.error("Authentication failed for user: %s", username)
                form.add_error(None, "Invalid username or password")
        else:
            logger.error("Form is not valid: %s", form.errors)
    else:
        form = DoctorLoginForm()
    return render(request, './doctor_login.html', {'form': form})

def nurse_login(request):
    if request.method == 'POST':
        form = NurseLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    nurse = Nurse.objects.get(user=user)
                    login(request, user)
                    return redirect('nurse_dashboard')
                except Nurse.DoesNotExist:
                    logger.error("User %s is not a nurse", username)
                    form.add_error(None, "Invalid username or password")
            else:
                logger.error("Authentication failed for user: %s", username)
                form.add_error(None, "Invalid username or password")
        else:
            logger.error("Form is not valid: %s", form.errors)
    else:
        form = NurseLoginForm()
    return render(request, './nurse_login.html', {'form': form})

def receptionist_login(request):
    if request.method == 'POST':
        form = ReceptionistLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    receptionist = Receptionist.objects.get(user=user)
                    login(request, user)
                    return redirect('receptionist_dashboard')
                except Receptionist.DoesNotExist:
                    logger.error("User %s is not a receptionist", username)
                    form.add_error(None, "Invalid username or password")
            else:
                logger.error("Authentication failed for user: %s", username)
                form.add_error(None, "Invalid username or password")
        else:
            logger.error("Form is not valid: %s", form.errors)
    else:
        form = ReceptionistLoginForm()
    return render(request, './receptionist_login.html', {'form': form})

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_appointment_created_email(appointment):
    """Send email notification when a patient creates a new appointment"""
    subject = 'Your Appointment has been Scheduled'
    
    # Context for email template
    context = {
        'patient_name': appointment.patient.user.get_full_name() or appointment.patient.user.username,
        'doctor_name': f"Dr. {appointment.doctor.user.get_full_name() or appointment.doctor.user.username}",
        'date': appointment.date.strftime('%A, %B %d, %Y'),
        'time': appointment.date.strftime('%I:%M %p'),
        'reason': appointment.reason,
        'status': appointment.status,
    }
    
    # Render HTML content
    html_content = render_to_string('emails/appointment_created.html', context)
    text_content = strip_tags(html_content)
    
    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[appointment.patient.user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    logger.info(f"Appointment created email sent to {appointment.patient.user.email}")

def send_appointment_approved_email(appointment):
    """Send email notification when a patient's appointment is approved"""
    subject = 'Your Appointment has been Approved'
    
    context = {
        'patient_name': appointment.patient.user.get_full_name() or appointment.patient.user.username,
        'doctor_name': f"Dr. {appointment.doctor.user.get_full_name() or appointment.doctor.user.username}",
        'date': appointment.date.strftime('%A, %B %d, %Y'),
        'time': appointment.date.strftime('%I:%M %p'),
        'reason': appointment.reason,
    }
    
    html_content = render_to_string('emails/appointment_approved.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[appointment.patient.user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    logger.info(f"Appointment approved email sent to {appointment.patient.user.email}")

def send_diagnosis_completed_email(diagnosis):
    """Send email notification when diagnosis and insights are completed"""
    subject = 'Your Medical Diagnosis and Recommendations'
    
    # Get related objects
    appointment = diagnosis.appointment
    prescription = Prescription.objects.filter(diagnosis=diagnosis).first()
    insight = Insight.objects.filter(diagnosis=diagnosis).first()
    invoice = Invoice.objects.filter(appointment=appointment).first()
    
    patient_advice = insight.patient_insights.split('\n') if insight and insight.patient_insights else []
    
    context = {
        'patient_name': diagnosis.patient.user.get_full_name() or diagnosis.patient.user.username,
        'doctor_name': f"Dr. {diagnosis.doctor.user.get_full_name() or diagnosis.doctor.user.username}",
        'diagnosis': diagnosis.diagnosis_text,
        'inpatient_advice': diagnosis.inpatient_advice,
        'patient_advice': patient_advice,
        'medication': prescription.medication if prescription else None,
        'dosage': prescription.dosage if prescription else None,
        'frequency': prescription.frequency if prescription else None,
        'invoice_amount': invoice.amount if invoice else None,
        'invoice_details': invoice.details if invoice else None,
    }
    
    html_content = render_to_string('emails/diagnosis_completed.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[diagnosis.patient.user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    logger.info(f"Diagnosis completed email sent to {diagnosis.patient.user.email}")
@login_required
def patient_dashboard(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    return render(request, './patient_dashboard.html', {'appointments': appointments})

@login_required
def doctor_dashboard(request):
    form = DoctorDashboardForm(request.POST or None)
    doctor = request.user.doctor
    
    # Set default date to today if no date is selected
    selected_date = datetime.now().date()
    
    # Process filter form if submitted
    if request.method == 'POST' and form.is_valid():
        selected_date = form.cleaned_data['date']
    
    # Get time slots and appointments for the selected date
    time_slots = TimeSlot.objects.filter(doctor=doctor, date=selected_date).order_by('start_time')
    appointments = Appointment.objects.filter(doctor=doctor, date__date=selected_date).order_by('date')
    
    # Get some overall statistics for the cards
    pending_count = Appointment.objects.filter(doctor=doctor, status='Pending').count()
    approved_count = Appointment.objects.filter(doctor=doctor, status='Approved').count()
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    
    context = {
        'form': form,
        'time_slots': time_slots,
        'appointments': appointments,
        'selected_date': selected_date,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'total_appointments': total_appointments,
    }
    
    return render(request, './doctor_dashboard.html', context)

@login_required
def nurse_dashboard(request):
    return render(request, './nurse_dashboard.html')

@login_required
def receptionist_dashboard(request):
    return render(request, './receptionist_dashboard.html')

def staff_login(request):
    return render(request, './staff_login.html')



def user_logout(request):
    logout(request)
    return redirect('hello')


# views.py
from django.http import JsonResponse
from .models import TimeSlot

def get_available_timeslots(request):
    doctor_id = request.GET.get('doctor_id')
    if doctor_id:
        # Use the utility function to get filtered time slots
        time_slots = get_filtered_available_timeslots(doctor_id)
        
        data = [
            {
                'id': ts.id,
                'label': f"{ts.date.strftime('%a, %b %d, %Y')} at {ts.start_time.strftime('%I:%M %p')}"
            }
            for ts in time_slots
        ]
        return JsonResponse({'time_slots': data})
    return JsonResponse({'time_slots': []})


@login_required
def make_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient
            time_slot = form.cleaned_data['time_slot']
            appointment.date = datetime.combine(time_slot.date, time_slot.start_time)
            appointment.duration = timedelta(minutes=60)
            appointment.save()
            send_appointment_created_email(appointment)
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    return render(request, './make_appointment.html', {'form': form})


@login_required
def approve_appointment(request, appointment_id):
    if not hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')
        
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.status = 'Approved'
    appointment.save()
    
    # Send approval email
    send_appointment_approved_email(appointment)
    
    return redirect('doctor_dashboard')

logger = logging.getLogger(__name__)

@login_required
def doctor_availability(request):
    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            doctor = request.user.doctor

            current_time = datetime.combine(date, start_time)
            end_time = datetime.combine(date, end_time)

            while current_time + timedelta(minutes=45) <= end_time:
                timeslot = TimeSlot(
                    doctor=doctor,
                    date=date,
                    start_time=current_time.time(),
                    end_time=(current_time + timedelta(minutes=45)).time(),
                    label=f"{current_time.time()} - {(current_time + timedelta(minutes=45)).time()}"
                )
                timeslot.save()
                logger.info(f"Created timeslot: {timeslot}")
                current_time += timedelta(minutes=45)

            return redirect('doctor_dashboard')
        else:
            logger.error(f"Form is not valid: {form.errors}")
    else:
        form = DoctorAvailabilityForm()
    return render(request, './doctor_availability.html', {'form': form})


import logging

logger = logging.getLogger(__name__)


@login_required
def create_diagnosis(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        diagnosis_form = DiagnosisForm(request.POST, doctor=request.user.doctor)
        if diagnosis_form.is_valid():
            diagnosis = diagnosis_form.save(commit=False)
            diagnosis.doctor = request.user.doctor
            diagnosis.patient = appointment.patient
            diagnosis.appointment = appointment
            diagnosis.save()
            logger.info(f"Diagnosis saved: {diagnosis}")

            # Create a Prescription object
            Prescription.objects.create(
                diagnosis=diagnosis,
                medication=diagnosis_form.cleaned_data['medication'],
                dosage=diagnosis_form.cleaned_data['dosage'],
                frequency=diagnosis_form.cleaned_data['frequency']
            )
            logger.info("Prescription created")

            # Calculate the invoice amount
            flat_rate = 1500
            admission_charge = 0
            if diagnosis.inpatient_advice and diagnosis.admission_date and diagnosis.discharge_date:
                days_admitted = (diagnosis.discharge_date - diagnosis.admission_date).days
                admission_charge = days_admitted * 2000

            total_amount = flat_rate + admission_charge

            # Create an Invoice object
            invoice = Invoice.objects.create(
                patient=diagnosis.patient,
                appointment=appointment,
                amount=total_amount,
                details=f"Appointment charge: {flat_rate} KES. Admission charge: {admission_charge} KES."
            )
            logger.info(f"Invoice created: {invoice}")

            # Generate insights using Groq API
            try:
                insights = generate_insights(diagnosis.diagnosis_text)
                
                # Save insights to the database
                insight = Insight.objects.create(
                    diagnosis=diagnosis,
                    doctor_insights="\n".join(insights["doctor_actions"]),
                    patient_insights="\n".join(insights["patient_advice"])
                )
                logger.info(f"Insights created: {insight}")
                
                
                send_diagnosis_completed_email(diagnosis)
                
                # Redirect to the diagnosis insights page
                return redirect('diagnosis_insights', diagnosis_id=diagnosis.id)
            except Exception as e:
                logger.error(f"Error generating insights: {e}")
                return redirect('doctor_diagnoses')
            
        else:
            logger.error(f"Form is not valid: {diagnosis_form.errors}")
    else:
        diagnosis_form = DiagnosisForm(doctor=request.user.doctor)

    return render(request, './create_diagnosis.html', {'appointment': appointment, 'diagnosis_form': diagnosis_form})

@login_required
def doctor_diagnoses(request):
    doctor = request.user.doctor
    diagnoses = Diagnosis.objects.filter(doctor=doctor).order_by('-appointment__date')
    return render(request, './doctor_diagnoses.html', {'diagnoses': diagnoses})

@login_required
def patient_appointments(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('date')
    return render(request, 'patient_appointments.html', {'appointments': appointments})

@login_required
def appointment_details(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, patient=request.user.patient)
    diagnosis = Diagnosis.objects.filter(appointment=appointment).first()
    prescription = Prescription.objects.filter(diagnosis=diagnosis).first() if diagnosis else None
    
    # Fix: Get insights related to the diagnosis
    insight = Insight.objects.filter(diagnosis=diagnosis).first() if diagnosis else None
    
    # Get patient-specific advice if insight exists
    patient_advice = insight.patient_insights.split('\n') if insight and insight.patient_insights else []
    
    invoice = Invoice.objects.filter(appointment=appointment).first()
    
    return render(request, 'appointment_details.html', {
        'appointment': appointment, 
        'diagnosis': diagnosis, 
        'prescription': prescription, 
        'invoice': invoice,
        'insight': insight,
        'patient_advice': patient_advice
    })

@login_required
def diagnosis_insights(request, diagnosis_id):
    diagnosis = Diagnosis.objects.get(id=diagnosis_id)
    
    # Check if the logged-in user is the doctor who made the diagnosis
    if request.user.doctor != diagnosis.doctor:
        return redirect('doctor_dashboard')
    
    insight = Insight.objects.filter(diagnosis=diagnosis).first()
    
    if insight:
        doctor_actions = insight.doctor_insights.split('\n') if insight.doctor_insights else []
        patient_advice = insight.patient_insights.split('\n') if insight.patient_insights else []
    else:
        doctor_actions = []
        patient_advice = []
    
    return render(request, 'diagnosis_insights.html', {
        'diagnosis': diagnosis,
        'doctor_actions': doctor_actions,
        'patient_advice': patient_advice
    })
    
@login_required
def doctor_appointments(request):
    """View for doctors to see and manage all their appointments"""
    if not hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')
        
    doctor = request.user.doctor
    
    # Filter options
    status_filter = request.GET.get('status', 'All')
    date_filter = request.GET.get('date', None)
    
    # Base query
    appointments = Appointment.objects.filter(doctor=doctor)
    
    # Apply filters
    if status_filter != 'All':
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date__date=filter_date)
        except ValueError:
            pass
    
    # Default ordering
    appointments = appointments.order_by('-date')
    
    # Update appointment status if form was submitted
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')
        
        if appointment_id and new_status in ['Pending', 'Approved', 'Denied']:
            try:
                appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
                old_status = appointment.status
                appointment.status = new_status
                appointment.save()
                
                # Send email notification if status changed to Approved
                if new_status == 'Approved' and old_status != 'Approved':
                    send_appointment_approved_email(appointment)
                    
                logger.info(f"Appointment {appointment_id} status updated to {new_status}")
                return redirect('doctor_appointments')
            except Appointment.DoesNotExist:
                logger.error(f"Appointment {appointment_id} not found or does not belong to the logged-in doctor")
    
    return render(request, 'doctor_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter
    })