# Generated by Django 2.2.1 on 2019-08-29 15:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20190829_2324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='etccardchargehistory',
            options={'ordering': ['-charged_on', '-created_on']},
        ),
        migrations.AddField(
            model_name='etccardchargehistory',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etccardchargehistory',
            name='charged_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]