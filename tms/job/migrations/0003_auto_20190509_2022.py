# Generated by Django 2.2.1 on 2019-05-09 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0002_auto_20190509_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='mission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.OrderProductDeliver'),
        ),
    ]
