from django.db.models import Q
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Patient, Doctor, Nurse, Receptionist, Appointment, TimeSlot, Diagnosis, Prescription
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
        fields = ['doctor', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].label = "Select Doctor"
        
        # If a doctor is selected in POST data
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                
                # Use the utility function to get filtered time slots
                from .views import get_filtered_available_timeslots  # Import the utility function
                self.fields['time_slot'].queryset = get_filtered_available_timeslots(doctor_id)
                
                # Set display format for time slots
                self.fields['time_slot'].label_from_instance = lambda obj: (
                    f"{obj.date.strftime('%a, %b %d, %Y')} at {obj.start_time.strftime('%I:%M %p')}"
                )
                
            except (ValueError, TypeError) as e:
                # Log the error for debugging
                print(f"Error in appointment form: {e}")
                # Invalid input from the client; fallback to empty queryset
                pass
                
        # For editing existing appointments
        elif self.instance.pk:
            doctor_id = self.instance.doctor_id
            appointment_datetime = self.instance.date
            
            if appointment_datetime:
                # Find the matching time slot for the existing appointment
                time_slots = TimeSlot.objects.filter(
                    doctor_id=doctor_id,
                    date=appointment_datetime.date(),
                    start_time=appointment_datetime.time()
                )
                self.fields['time_slot'].queryset = time_slots
                self.fields['time_slot'].label_from_instance = lambda obj: (
                    f"{obj.date.strftime('%a, %b %d, %Y')} at {obj.start_time.strftime('%I:%M %p')}"
                )
    
    def save(self, commit=True):
        # Override save to handle the time_slot field properly
        appointment = super().save(commit=False)
        
        # Get the selected time_slot and set date/time accordingly
        time_slot = self.cleaned_data.get('time_slot')
        if time_slot:
            # Combine the date and start_time from the time_slot
            appointment.date = datetime.combine(time_slot.date, time_slot.start_time)
            appointment.duration = timedelta(minutes=60)  # Set standard duration
        
        if commit:
            appointment.save()
        
        return appointment

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
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.order_by(), required=True, label="Select Appointment")
    medication = forms.CharField(max_length=100, required=True, label="Medication")
    dosage = forms.CharField(max_length=100, required=True, label="Dosage")
    frequency = forms.CharField(max_length=100, required=True, label="Frequency")
    admission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Admission Date")
    discharge_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Discharge Date")

    class Meta:
        model = Diagnosis
        fields = ['appointment', 'diagnosis_text', 'inpatient_advice', 'admission_date', 'discharge_date', 'medication', 'dosage', 'frequency']

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        appointment_id = kwargs.pop('appointment_id', None)
        super().__init__(*args, **kwargs)
        
        if doctor:
            # Filter appointments by doctor
            self.fields['appointment'].queryset = Appointment.objects.filter(
                doctor=doctor, 
                status='Approved'
            ).order_by('-date')
            
            # If a specific appointment was requested, pre-select it
            if appointment_id:
                try:
                    # Try to get the specific appointment
                    appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
                    
                    # Make sure this appointment is in the queryset
                    if appointment in self.fields['appointment'].queryset:
                        # Pre-select this appointment in the form
                        self.fields['appointment'].initial = appointment
                        
                        # Optionally disable the field to prevent changing
                        self.fields['appointment'].widget.attrs['disabled'] = True
                        self.fields['appointment'].widget.attrs['readonly'] = True
                        
                        # Store the original value to use in clean method
                        self.appointment_id = appointment_id
                    
                except Appointment.DoesNotExist:
                    pass
    
    def clean(self):
        cleaned_data = super().clean()
        
        # If the appointment field was disabled, it won't be in cleaned_data
        # We need to restore it from our stored value
        if hasattr(self, 'appointment_id') and 'appointment' not in cleaned_data:
            try:
                appointment = Appointment.objects.get(id=self.appointment_id)
                cleaned_data['appointment'] = appointment
            except Appointment.DoesNotExist:
                pass
                
        return cleaned_data