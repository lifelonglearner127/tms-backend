# Generated by Django 2.2.1 on 2019-07-15 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='loading_weight',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='mission',
            name='mission_weight',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='mission',
            name='unloading_weight',
            field=models.FloatField(default=0),
        ),
    ]
