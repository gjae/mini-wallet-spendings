# Generated by Django 3.1 on 2020-08-16 00:08

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocktaking', '0002_walletplatform_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPlatform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('trash', 'trash')], default='active', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('description', models.CharField(blank=True, max_length=90)),
                ('initial_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=23)),
                ('spent_total_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=23)),
                ('earning_total_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=23)),
                ('last_movement', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_has_wallet', to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallet_belongs_user', to='stocktaking.walletplatform')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
