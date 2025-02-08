from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Patient, Doctor, Nurse, Receptionist, Appointment, TimeSlot, Diagnosis
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils.timezone import is_aware, make_naive
from . import views
class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'address', 'date_of_birth', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            patient = Patient(user=user, date_of_birth=self.cleaned_data['date_of_birth'], address=self.cleaned_data['address'])
            patient.save()
        return user

class PatientLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput)

class DoctorLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput)

class NurseLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput)

class ReceptionistLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput)




# Form for creating or updating an appointment
class AppointmentForm(forms.ModelForm):
    time_slot = forms.ModelChoiceField(queryset=TimeSlot.objects.none(), required=True, label="Available Time Slots")

    class Meta:
        model = Appointment
        fields = ['doctor', 'time_slot', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].label = "Select Doctor"
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['time_slot'].queryset = TimeSlot.objects.filter(doctor_id=doctor_id).order_by('date', 'start_time')
                self.fields['time_slot'].label_from_instance = lambda obj: obj.get_label()
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['time_slot'].queryset = TimeSlot.objects.filter(doctor=self.instance.doctor).order_by('date', 'start_time')
            self.fields['time_slot'].label_from_instance = lambda obj: obj.get_label()

class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['start_time'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['end_time'].widget = forms.TimeInput(attrs={'type': 'time'})



class DoctorDashboardForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Select Date")



class DiagnosisForm(forms.ModelForm):
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.none(), required=True, label="Select Appointment")

    class Meta:
        model = Diagnosis
        fields = ['appointment', 'diagnosis_text', 'inpatient_advice']

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields['appointment'].queryset = Appointment.objects.filter(doctor=doctor).order_by('date')