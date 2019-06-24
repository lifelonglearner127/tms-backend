# Generated by Django 2.2.1 on 2019-06-24 01:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('info', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('alias', models.CharField(max_length=100)),
                ('order_source', models.CharField(choices=[('I', '内部'), ('C', 'App')], default='I', max_length=1)),
                ('status', models.CharField(choices=[('P', '未开始'), ('I', '已开始'), ('C', '已完成')], default='P', max_length=1)),
                ('assignee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='charge_orders', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated'],
            },
        ),
        migrations.CreateModel(
            name='OrderLoadingStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_time', models.DateTimeField()),
                ('loading_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loading_stations', to='info.Station')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_weight', models.DecimalField(decimal_places=3, max_digits=7)),
                ('total_weight_measure_unit', models.CharField(choices=[('L', '公升'), ('T', '吨')], default='T', max_length=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('price_weight_measure_unit', models.CharField(choices=[('L', '公升'), ('T', '吨')], default='T', max_length=1)),
                ('loss', models.DecimalField(decimal_places=3, default=0, max_digits=7)),
                ('loss_unit', models.CharField(choices=[('L', '公升'), ('T', '吨')], default='T', max_length=2)),
                ('payment_method', models.CharField(choices=[('T', '吨'), ('D', '吨/公里'), ('P', '一口价')], default='T', max_length=1)),
                ('is_split', models.BooleanField(default=False)),
                ('is_pump', models.BooleanField(default=False)),
                ('order_loading_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.OrderLoadingStation')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.Product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProductDeliver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_time', models.DateTimeField()),
                ('weight', models.PositiveIntegerField()),
                ('order_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.OrderProduct')),
                ('unloading_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.Station')),
            ],
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='unloading_stations',
            field=models.ManyToManyField(through='order.OrderProductDeliver', to='info.Station'),
        ),
        migrations.AddField(
            model_name='orderloadingstation',
            name='products',
            field=models.ManyToManyField(through='order.OrderProduct', to='info.Product'),
        ),
        migrations.AddField(
            model_name='orderloadingstation',
            name='quality_station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unloading_stations', to='info.Station'),
        ),
        migrations.AddField(
            model_name='order',
            name='loading_stations',
            field=models.ManyToManyField(through='order.OrderLoadingStation', to='info.Station'),
        ),
    ]
