from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Doctor, Nurse, Receptionist

# Register the custom User model with the UserAdmin
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Receptionist)