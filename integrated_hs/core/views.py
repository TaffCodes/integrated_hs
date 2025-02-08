import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PatientRegistrationForm, PatientLoginForm, DoctorLoginForm, NurseLoginForm, ReceptionistLoginForm, AppointmentForm, DoctorAvailabilityForm, DoctorDashboardForm, DiagnosisForm
from .models import Patient, Doctor, Nurse, Receptionist, Appointment, TimeSlot, Diagnosis
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils.timezone import is_naive, make_naive


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

@login_required
def patient_dashboard(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('date')
    return render(request, './patient_dashboard.html', {'appointments': appointments})

@login_required
def doctor_dashboard(request):
    form = DoctorDashboardForm(request.POST or None)
    time_slots = None
    appointments = None

    if request.method == 'POST' and form.is_valid():
        date = form.cleaned_data['date']
        doctor = request.user.doctor
        time_slots = TimeSlot.objects.filter(doctor=doctor, date=date).order_by('start_time')
        appointments = Appointment.objects.filter(doctor=doctor, date__date=date).order_by('date')

    return render(request, './doctor_dashboard.html', {'form': form, 'time_slots': time_slots, 'appointments': appointments})


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
        time_slots = TimeSlot.objects.filter(doctor_id=doctor_id).order_by('date', 'start_time')
        data = [
            {
                'id': ts.id,
                'label': ts.get_label(),  # assuming you have a method get_label() that formats the slot
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
            appointment.duration = timedelta(minutes=45)
            appointment.save()
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    return render(request, './make_appointment.html', {'form': form})



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


@login_required
def doctor_dashboard(request):
    form = DoctorDashboardForm(request.POST or None)
    time_slots = None
    appointments = None

    if request.method == 'POST' and form.is_valid():
        date = form.cleaned_data['date']
        doctor = request.user.doctor
        time_slots = TimeSlot.objects.filter(doctor=doctor, date=date).order_by('start_time')
        appointments = Appointment.objects.filter(doctor=doctor, date__date=date).order_by('date')
        return render(request, './appointments.html', {'date': date, 'appointments': appointments})

    return render(request, './doctor_dashboard.html', {'form': form, 'time_slots': time_slots, 'appointments': appointments})

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
            return redirect('doctor_dashboard')
    else:
        diagnosis_form = DiagnosisForm(doctor=request.user.doctor)

    return render(request, './create_diagnosis.html', {'appointment': appointment, 'diagnosis_form': diagnosis_form})

@login_required
def doctor_diagnoses(request):
    doctor = request.user.doctor
    diagnoses = Diagnosis.objects.filter(doctor=doctor).order_by('appointment__date')
    return render(request, './doctor_diagnoses.html', {'diagnoses': diagnoses})