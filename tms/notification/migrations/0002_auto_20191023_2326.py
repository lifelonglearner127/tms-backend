# Generated by Django 2.2.1 on 2019-10-23 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.PositiveIntegerField(choices=[(0, '驾驶证'), (1, '车辆行驶证'), (2, '车辆运营证'), (3, '车辆保险')], default=0),
        ),
    ]
