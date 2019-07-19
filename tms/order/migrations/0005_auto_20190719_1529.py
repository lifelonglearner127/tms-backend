# Generated by Django 2.2.1 on 2019-07-19 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_auto_20190719_0719'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobbill',
            options={'ordering': ['category', 'sub_category', 'detail_category']},
        ),
        migrations.RenameField(
            model_name='jobstationproduct',
            old_name='bill',
            new_name='document',
        ),
        migrations.RemoveField(
            model_name='jobbill',
            name='bill',
        ),
        migrations.AddField(
            model_name='jobbill',
            name='document',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='jobbill',
            name='category',
            field=models.PositiveIntegerField(choices=[(0, '加油'), (1, '路票'), (2, '其他')], default=0),
        ),
    ]
