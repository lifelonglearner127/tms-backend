# Generated by Django 2.2.1 on 2019-11-07 16:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('info', '0001_initial'),
        ('hr', '0001_initial'),
        ('vehicle', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('category', models.CharField(choices=[(0, '吃饭'), (1, '停车'), (2, '洗车'), (3, '住宿')], default=0, max_length=1)),
                ('from_time', models.DateTimeField()),
                ('to_time', models.DateTimeField()),
                ('cost', models.FloatField(default=0)),
                ('description', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ETCCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_child', models.BooleanField(default=False)),
                ('issue_company', models.CharField(max_length=100)),
                ('issued_on', models.DateField(blank=True, null=True)),
                ('number', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('last_charge_date', models.DateField(blank=True, null=True)),
                ('balance', models.FloatField(default=0)),
                ('description', models.TextField(blank=True, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.Department')),
                ('master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='finance.ETCCard')),
                ('vehicle', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vehicle.Vehicle')),
            ],
            options={
                'ordering': ['-last_charge_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FuelCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_child', models.BooleanField(default=False)),
                ('issue_company', models.CharField(max_length=100)),
                ('issued_on', models.DateField(blank=True, null=True)),
                ('number', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('last_charge_date', models.DateField(blank=True, null=True)),
                ('balance', models.FloatField(default=0)),
                ('description', models.TextField(blank=True, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.Department')),
                ('master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='finance.FuelCard')),
                ('vehicle', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vehicle.Vehicle')),
            ],
            options={
                'ordering': ['-last_charge_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FuelCardChargeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_amount', models.FloatField(default=0)),
                ('charged_amount', models.FloatField(default=0)),
                ('after_amount', models.FloatField(default=0)),
                ('charged_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.FuelCard')),
            ],
            options={
                'ordering': ['-charged_on', '-created_on'],
            },
        ),
        migrations.CreateModel(
            name='FuelBillHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_card', models.BooleanField(default=False)),
                ('unit_price', models.FloatField(default=0)),
                ('amount', models.FloatField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('address', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('paid_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.FuelCard')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('oil_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.Station')),
            ],
            options={
                'ordering': ['-paid_on', '-created_on'],
            },
        ),
        migrations.CreateModel(
            name='FuelBillDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ImageField(upload_to='')),
                ('fuel_bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='finance.FuelBillHistory')),
            ],
        ),
        migrations.CreateModel(
            name='ETCCardChargeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_amount', models.FloatField(default=0)),
                ('charged_amount', models.FloatField(default=0)),
                ('after_amount', models.FloatField(default=0)),
                ('charged_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.ETCCard')),
            ],
            options={
                'ordering': ['-charged_on', '-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ETCBillHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_card', models.BooleanField(default=False)),
                ('amount', models.FloatField(default=0)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('paid_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.ETCCard')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-paid_on', '-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ETCBillDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ImageField(upload_to='')),
                ('etc_bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='finance.ETCBillHistory')),
            ],
        ),
        migrations.CreateModel(
            name='BillDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ImageField(upload_to='')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='finance.Bill')),
            ],
        ),
    ]
