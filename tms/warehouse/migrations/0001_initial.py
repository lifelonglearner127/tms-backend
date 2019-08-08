# Generated by Django 2.2.1 on 2019-08-02 16:04

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
            name='WarehouseProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('amount', models.FloatField(default=0)),
                ('amount_unit', models.CharField(choices=[('K', '公斤'), ('T', '吨')], max_length=1)),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OutTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(default=0)),
                ('amount_unit', models.CharField(choices=[('K', '公斤'), ('T', '吨')], max_length=1)),
                ('transaction_on', models.DateTimeField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='out_transactions', to='warehouse.WarehouseProduct')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('unit_price', models.FloatField(default=0)),
                ('amount', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('amount_unit', models.CharField(choices=[('K', '公斤'), ('T', '吨')], max_length=1)),
                ('supplier', models.CharField(max_length=100)),
                ('supplier_contact', models.CharField(max_length=100)),
                ('supplier_mobile', models.CharField(max_length=100)),
                ('transaction_on', models.DateTimeField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_transactions', to='warehouse.WarehouseProduct')),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
    ]