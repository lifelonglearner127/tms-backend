# Generated by Django 2.2.1 on 2019-12-04 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_auto_20191127_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpayment',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]