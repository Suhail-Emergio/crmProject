# Generated by Django 4.2.5 on 2024-12-26 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration', models.IntegerField()),
                ('internship', models.CharField(max_length=100)),
                ('rate', models.IntegerField()),
                ('gst', models.IntegerField()),
                ('total_rate', models.IntegerField()),
                ('syllabus', models.FileField(upload_to='course/')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strength', models.IntegerField()),
                ('total_lead', models.IntegerField(default=0)),
                ('todays_lead', models.IntegerField(default=0)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_admin', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('whatsapp', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(max_length=100)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('assign_status', models.BooleanField(default=False)),
                ('lead_status', models.BooleanField(default=False)),
                ('campain', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=False)),
                ('trash', models.BooleanField(default=False)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Won',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('Course', 'Course'), ('Internship', 'Internship')], max_length=100)),
                ('type', models.CharField(choices=[('Online', 'Online'), ('Offline', 'Offline')], max_length=100)),
                ('won_on', models.DateField(auto_now=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='crmAdmin.course')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crmAdmin.employee')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crmAdmin.lead')),
            ],
        ),
        migrations.CreateModel(
            name='TrashLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lost', models.BooleanField(default=False)),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Daily', 'Daily'), ('Monthly', 'Monthly')], max_length=100)),
                ('target', models.IntegerField()),
                ('target_won', models.IntegerField(default=0)),
                ('target_remaining', models.IntegerField(default=0)),
                ('date', models.DateField()),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.employee')),
            ],
        ),
        migrations.CreateModel(
            name='SaleReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('total', models.IntegerField(default=0)),
                ('follow', models.IntegerField(default=0)),
                ('Notanswer', models.IntegerField(default=0)),
                ('Notinterested', models.IntegerField(default=0)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('csv', models.FileField(upload_to='report')),
                ('created_on', models.DateField(auto_now=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.CharField(max_length=100)),
                ('screenshot', models.FileField(upload_to='media/')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crmAdmin.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Leadstatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.CharField(choices=[('Not Contacted Yet', 'Not Contacted Yet'), ('Not Answering', 'Not Answering'), ('Busy', 'Busy'), ('Contacted', 'Contacted:Waiting For Reply'), ('Got Appointment', 'Got Appointment'), ('Payment', 'Payment'), ('Not Interested', 'Not Interested')], default='Not Contacted Yet', max_length=100)),
                ('status', models.CharField(choices=[('Not Answering', 'Not Answering'), ('Follow Up', 'Follow Up'), ('Won', 'Won'), ('Lost', 'Lost')], default='Not Answering', max_length=100)),
                ('probability', models.CharField(max_length=100)),
                ('notes', models.TextField()),
                ('contacted_on', models.DateField(auto_now=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crmAdmin.course')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Duty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_date', models.DateField()),
                ('created_on', models.DateField(auto_now=True)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.employee')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmAdmin.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Callback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('note', models.TextField()),
                ('status', models.BooleanField(default=False)),
                ('duty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duty', to='crmAdmin.duty')),
            ],
        ),
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.IntegerField()),
                ('target_won', models.IntegerField(default=0)),
                ('superadmin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superadmin', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
