from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Patient, Doctor, Nurse, Receptionist, Appointment, Diagnosis
from django.core.exceptions import ValidationError
from datetime import datetime

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

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'reason']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < datetime.now():
            raise ValidationError("The date cannot be in the past.")
        return date