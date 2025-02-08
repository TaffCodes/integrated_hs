import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PatientRegistrationForm, PatientLoginForm, DoctorLoginForm, NurseLoginForm, ReceptionistLoginForm
from .models import Patient, Doctor, Nurse, Receptionist

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
    return render(request, './patient_dashboard.html')

@login_required
def doctor_dashboard(request):
    return render(request, './doctor_dashboard.html')

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