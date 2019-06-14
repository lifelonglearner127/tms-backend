# Generated by Django 2.2.1 on 2019-06-14 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobbilldocument',
            name='category',
            field=models.PositiveIntegerField(choices=[(0, 'Bill from Loading Station'), (1, 'Bill from Quality Station'), (2, 'Bill from UnLoading Station'), (3, 'Bill from Oil Station'), (4, 'Bill from traffic')], default=0),
        ),
    ]
