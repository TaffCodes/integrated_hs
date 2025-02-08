from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('hello/', views.hello, name='hello'),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('patient_register/', views.patient_register, name='patient_register'),
    path('patient_login/', views.patient_login, name='patient_login'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('receptionist_dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path(('doctor_login/'), views.doctor_login, name='doctor_login'),
    path('nurse_login/', views.nurse_login, name='nurse_login'),
    path('receptionist_login/', views.receptionist_login, name='receptionist_login'),
    path('nurse_dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('make_appointment/', views.make_appointment, name='make_appointment'),
    path('doctor_availability/', views.doctor_availability, name='doctor_availability'),
    path('ajax/get_timeslots/', views.get_available_timeslots, name='get_timeslots'),
    path('appointments/', views.make_appointment, name='appointments'),
    path('create_diagnosis/<int:appointment_id>/', views.create_diagnosis, name='create_diagnosis'),
    path('doctor_diagnoses/', views.doctor_diagnoses, name='doctor_diagnoses'),
]