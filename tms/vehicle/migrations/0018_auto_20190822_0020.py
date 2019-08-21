# Generated by Django 2.2.1 on 2019-08-21 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0017_auto_20190821_2231'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehiclecheckhistory',
            old_name='description',
            new_name='after_driving_description',
        ),
        migrations.RenameField(
            model_name='vehiclecheckhistory',
            old_name='problems',
            new_name='after_driving_problems',
        ),
        migrations.AddField(
            model_name='vehiclecheckhistory',
            name='before_driving_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclecheckhistory',
            name='before_driving_problems',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vehiclecheckhistory',
            name='driving_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclecheckhistory',
            name='driving_problems',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
