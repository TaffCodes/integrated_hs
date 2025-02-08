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
]