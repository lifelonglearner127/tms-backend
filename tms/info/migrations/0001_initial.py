# Generated by Django 2.2.1 on 2019-06-14 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('G', '汽油'), ('O', '油')], db_index=True, default='G', max_length=10)),
                ('price', models.DecimalField(decimal_places=1, max_digits=5)),
                ('unit_weight', models.PositiveIntegerField(default=1)),
                ('measure_unit', models.CharField(choices=[('L', '公升'), ('T', '吨')], default='T', max_length=1)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-updated'],
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('contact', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=30)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('station_type', models.CharField(choices=[('L', '装货地'), ('U', '卸货地'), ('Q', '质检点'), ('O', '合作油站')], db_index=True, max_length=1)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('radius', models.PositiveIntegerField(blank=True, null=True)),
                ('product_category', models.CharField(choices=[('G', '汽油'), ('O', '油')], db_index=True, default='G', max_length=10)),
                ('price', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('working_time', models.PositiveIntegerField(blank=True, null=True)),
                ('working_time_measure_unit', models.CharField(choices=[('M', '分钟'), ('H', '小时')], default='H', max_length=1)),
                ('average_time', models.PositiveIntegerField(blank=True, null=True)),
                ('average_time_measure_unit', models.CharField(choices=[('M', '分钟'), ('H', '小时')], default='H', max_length=1)),
                ('price_vary_duration', models.PositiveIntegerField(blank=True, null=True)),
                ('price_vary_duration_unit', models.CharField(choices=[('W', '周'), ('M', '月'), ('Y', '年')], default='M', max_length=1)),
            ],
            options={
                'ordering': ['-updated'],
                'unique_together': {('longitude', 'latitude')},
            },
        ),
    ]
