# Generated by Django 2.2.1 on 2019-06-06 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('info', '0001_initial'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('alias', models.CharField(max_length=100)),
                ('order_source', models.CharField(choices=[('I', 'From Staff'), ('C', 'From Customer')], default='I', max_length=1)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('I', 'In Progress'), ('C', 'Complete')], default='P', max_length=1)),
                ('assignee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.StaffProfile')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.CustomerProfile')),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderLoadingStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_time', models.DateTimeField(blank=True, null=True)),
                ('loading_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loading_stations', to='info.Station')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_weight', models.PositiveIntegerField()),
                ('weight_unit', models.CharField(choices=[('T', 't'), ('K', 'Kg')], default='T', max_length=2)),
                ('loss', models.PositiveIntegerField(default=0)),
                ('loss_unit', models.CharField(choices=[('T', 't'), ('K', 'Kg')], default='T', max_length=2)),
                ('payment_unit', models.CharField(choices=[('T', 't'), ('K', 'Kg')], default='T', max_length=2)),
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
