# Generated by Django 2.2.1 on 2019-08-30 10:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('security', '0004_testresult_full_point'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityLibrary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('is_all', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('departments', models.ManyToManyField(to='hr.Department')),
            ],
            options={
                'ordering': ('-updated',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SecurityLibraryAttachments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.FileField(upload_to='')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='security.SecurityLibrary')),
            ],
        ),
        migrations.CreateModel(
            name='SecurityLearningProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField()),
                ('finish_time', models.DateTimeField()),
                ('place', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('audiences', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
