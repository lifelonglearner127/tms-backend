# Generated by Django 2.2.1 on 2019-08-30 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0013_auto_20190830_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuelcardusagehistory',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.FuelCard'),
        ),
    ]