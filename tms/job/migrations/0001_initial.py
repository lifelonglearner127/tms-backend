# Generated by Django 2.2.1 on 2019-06-25 16:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle', '0001_initial'),
        ('order', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('road', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.PositiveIntegerField(default=1)),
                ('start_due_time', models.DateTimeField(blank=True, null=True)),
                ('finish_due_time', models.DateTimeField(blank=True, null=True)),
                ('started_on', models.DateTimeField(blank=True, null=True)),
                ('arrived_loading_station_on', models.DateTimeField(blank=True, null=True)),
                ('started_loading_on', models.DateTimeField(blank=True, null=True)),
                ('finished_loading_on', models.DateTimeField(blank=True, null=True)),
                ('departure_loading_station_on', models.DateTimeField(blank=True, null=True)),
                ('arrived_quality_station_on', models.DateTimeField(blank=True, null=True)),
                ('started_checking_on', models.DateTimeField(blank=True, null=True)),
                ('finished_checking_on', models.DateTimeField(blank=True, null=True)),
                ('departure_quality_station_on', models.DateTimeField(blank=True, null=True)),
                ('finished_on', models.DateTimeField(blank=True, null=True)),
                ('total_weight', models.PositiveIntegerField()),
                ('total_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('empty_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('heavy_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('highway_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('normalway_mileage', models.PositiveIntegerField(blank=True, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_driver', to=settings.AUTH_USER_MODEL)),
                ('escort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_escort', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParkingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_time', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_time', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_requests_as_driver', to=settings.AUTH_USER_MODEL)),
                ('escort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_requests_as_escort', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='job.Job')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_requests', to='vehicle.Vehicle')),
            ],
            options={
                'ordering': ['approved', '-approved_time', '-request_time'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.PositiveIntegerField()),
                ('mission_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('loading_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('unloading_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('arrived_station_on', models.DateTimeField(blank=True, null=True)),
                ('started_unloading_on', models.DateTimeField(blank=True, null=True)),
                ('finished_unloading_on', models.DateTimeField(blank=True, null=True)),
                ('departure_station_on', models.DateTimeField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.Job')),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.OrderProductDeliver')),
            ],
            options={
                'ordering': ['step'],
            },
        ),
        migrations.AddField(
            model_name='job',
            name='missions',
            field=models.ManyToManyField(through='job.Mission', to='order.OrderProductDeliver'),
        ),
        migrations.AddField(
            model_name='job',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='order.Order'),
        ),
        migrations.AddField(
            model_name='job',
            name='route',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='road.Route'),
        ),
        migrations.AddField(
            model_name='job',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='vehicle.Vehicle'),
        ),
        migrations.CreateModel(
            name='EscortChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_time', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_time', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('change_time', models.DateTimeField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.Job')),
                ('new_escort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['approved', '-approved_time', '-request_time'],
                'unique_together': {('job', 'new_escort')},
            },
        ),
        migrations.CreateModel(
            name='DriverChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_time', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_time', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('change_time', models.DateTimeField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.Job')),
                ('new_driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['approved', '-approved_time', '-request_time'],
                'unique_together': {('job', 'new_driver')},
            },
        ),
    ]
