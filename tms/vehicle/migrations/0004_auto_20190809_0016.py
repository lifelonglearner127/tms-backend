# Generated by Django 2.2.1 on 2019-08-08 16:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicle', '0003_auto_20190809_0016'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleAfterDrivingCheckHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='VehicleDrivingCheckHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='VehicleDrivingItemCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_checked', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.VehicleCheckItem')),
                ('vehicle_check_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.VehicleDrivingCheckHistory')),
            ],
        ),
        migrations.AddField(
            model_name='vehicledrivingcheckhistory',
            name='check_items',
            field=models.ManyToManyField(through='vehicle.VehicleDrivingItemCheck', to='vehicle.VehicleCheckItem'),
        ),
        migrations.AddField(
            model_name='vehicledrivingcheckhistory',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicledrivingcheckhistory',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.Vehicle'),
        ),
        migrations.CreateModel(
            name='VehicleAfterDrivingItemCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_checked', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.VehicleCheckItem')),
                ('vehicle_check_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.VehicleAfterDrivingCheckHistory')),
            ],
        ),
        migrations.AddField(
            model_name='vehicleafterdrivingcheckhistory',
            name='check_items',
            field=models.ManyToManyField(through='vehicle.VehicleAfterDrivingItemCheck', to='vehicle.VehicleCheckItem'),
        ),
        migrations.AddField(
            model_name='vehicleafterdrivingcheckhistory',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicleafterdrivingcheckhistory',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.Vehicle'),
        ),
    ]