# Generated by Django 3.1 on 2020-08-16 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocktaking', '0003_userplatform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplatform',
            name='last_movement',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
