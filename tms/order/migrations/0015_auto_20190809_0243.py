# Generated by Django 2.2.1 on 2019-08-08 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_qualitycheck'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordercart',
            name='loading_station',
        ),
        migrations.RemoveField(
            model_name='ordercart',
            name='quality_station',
        ),
        migrations.RemoveField(
            model_name='ordercart',
            name='unit_price',
        ),
        migrations.RemoveField(
            model_name='ordercart',
            name='unloading_stations',
        ),
        migrations.DeleteModel(
            name='OrderCartUnloadingStation',
        ),
    ]