# Generated by Django 5.1.6 on 2025-02-11 11:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_invoice_appointment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_insights', models.TextField(help_text='Recommendations for the doctor based on the diagnosis.')),
                ('patient_insights', models.TextField(help_text='Recommendations for the patient based on the diagnosis.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('diagnosis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.diagnosis')),
            ],
        ),
    ]
