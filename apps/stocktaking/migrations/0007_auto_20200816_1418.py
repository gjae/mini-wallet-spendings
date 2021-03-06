# Generated by Django 3.1 on 2020-08-16 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocktaking', '0006_auto_20200816_0209'),
    ]

    operations = [
        migrations.AddField(
            model_name='userplatform',
            name='current_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=23),
        ),
        migrations.AlterField(
            model_name='movements',
            name='movement_type',
            field=models.CharField(choices=[('credit', 'credit'), ('debit', 'debit')], max_length=15),
        ),
    ]
