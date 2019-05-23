# Generated by Django 2.2.1 on 2019-05-23 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('account', '0001_initial'),
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.CharField(choices=[('NT', 'Not Started'), ('ST', 'Started'), ('TL', 'To Loading Station'), ('AL', 'Arrived at Loading Station'), ('DL', 'Departure at Loading Station'), ('TU', 'To UnLoading Station'), ('AU', 'Arrived at Unloading Station'), ('C', 'Complete')], default='NT', max_length=2)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('arrived_at_loading_station', models.DateTimeField(blank=True, null=True)),
                ('arrived_at_quality_station', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_primary', to='account.StaffProfile')),
                ('escort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_escort', to='account.StaffProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrived_at_unloading_station', models.DateTimeField(blank=True, null=True)),
                ('loading_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('unloading_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.Job')),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.OrderProductDeliver')),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='missions',
            field=models.ManyToManyField(through='job.Mission', to='order.OrderProductDeliver'),
        ),
        migrations.AddField(
            model_name='job',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.Vehicle'),
        ),
    ]
