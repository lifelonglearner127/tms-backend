# Generated by Django 2.2.1 on 2019-08-22 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0008_auto_20190821_1328'),
        ('order', '0019_auto_20190823_0310'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LoadingStationProduct',
            new_name='LoadingStationProductCheck',
        ),
    ]