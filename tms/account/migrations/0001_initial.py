# Generated by Django 2.2.1 on 2019-11-07 16:23

from django.db import migrations, models
import django.db.models.deletion
import tms.core.validations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('permissions', models.ManyToManyField(to='account.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=100, unique=True, validators=[tms.core.validations.validate_username])),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('mobile', models.CharField(blank=True, max_length=20, null=True, unique=True, validators=[tms.core.validations.validate_mobile])),
                ('device_token', models.CharField(blank=True, max_length=100, null=True)),
                ('channel_name', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user_type', models.CharField(choices=[('A', '管理人员'), ('S', '工作人员'), ('D', '驾驶人员'), ('E', '押运人员'), ('P', '外驾驶人员'), ('G', '外押运人员'), ('C', '客户'), ('T', '检查')], default='S', max_length=1)),
                ('permission', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.UserPermission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
