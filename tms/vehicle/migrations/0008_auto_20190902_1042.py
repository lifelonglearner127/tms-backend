# Generated by Django 2.2.1 on 2019-09-02 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0007_auto_20190901_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='actual_load',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='actual_load_2',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='total_load',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='total_load_2',
            field=models.FloatField(default=0),
        ),
    ]