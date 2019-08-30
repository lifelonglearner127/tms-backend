# Generated by Django 2.2.1 on 2019-08-30 04:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_auto_20190830_0241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fuelcardchargehistory',
            options={'ordering': ['-charged_on', '-created_on']},
        ),
        migrations.AlterModelOptions(
            name='fuelcardusagehistory',
            options={'ordering': ['-paid_on', '-created_on']},
        ),
        migrations.AddField(
            model_name='fuelcardchargehistory',
            name='after_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='fuelcardchargehistory',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fuelcardusagehistory',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fuelcardusagehistory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fuelcardusagehistory',
            name='unit_price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='fuelcardusagehistory',
            name='weight',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='etccardusagehistory',
            name='paid_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fuelcardchargehistory',
            name='charged_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fuelcardusagehistory',
            name='paid_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='FuelCardUsageDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ImageField(upload_to='')),
                ('fuel_usage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='finance.FuelCardUsageHistory')),
            ],
        ),
    ]
