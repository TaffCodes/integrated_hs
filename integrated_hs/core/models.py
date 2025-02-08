from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Updated related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Updated related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    address = models.TextField()

    def __str__(self):
        return self.user.username

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    availability = models.JSONField()  # Example: {"Monday": ["09:00", "17:00"], "Tuesday": ["09:00", "17:00"]}

    def __str__(self):
        return self.user.username

class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} {self.start_time} to {self.end_time}"

    def get_label(self):
        return f"{self.date} {self.start_time} - {self.end_time}"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.DurationField(default=timedelta(minutes=45))
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')])
    reason = models.TextField()

    def __str__(self):
        return f"Appointment {self.id} - {self.patient.user.username} with {self.doctor.user.username}"

class Diagnosis(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis_text = models.TextField()
    inpatient_advice = models.BooleanField(default=False)


    def __str__(self):
        return f"Diagnosis {self.id} for {self.patient.user.username}"

class Prescription(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)

    def __str__(self):
        return f"Prescription {self.id} for {self.diagnosis.patient.user.username}"

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Invoice {self.id} for {self.patient.user.username}"

class Comment(models.Model):
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} by {self.nurse.user.username} on {self.patient.user.username}"

class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_admitted = models.DateTimeField(auto_now_add=True)