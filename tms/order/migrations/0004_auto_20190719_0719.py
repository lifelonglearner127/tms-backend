# Generated by Django 2.2.1 on 2019-07-19 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20190719_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='bills',
            field=models.ManyToManyField(blank=True, to='order.JobBill'),
        ),
    ]
