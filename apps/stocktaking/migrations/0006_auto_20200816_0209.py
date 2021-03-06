# Generated by Django 3.1 on 2020-08-16 02:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stocktaking', '0005_userplatform_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=190, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=23)),
                ('platform_reference', models.CharField(max_length=15)),
                ('status', models.CharField(choices=[('completed', 'completed'), ('deferred', 'deferred'), ('blocked', 'blocked')], default='completed', max_length=20)),
                ('movement_type', models.CharField(choices=[('received', 'received'), ('payed', 'payed')], max_length=15)),
                ('platform_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_earnings', to='stocktaking.userplatform')),
            ],
        ),
        migrations.AddIndex(
            model_name='movements',
            index=models.Index(fields=['platform_reference'], name='platform_reference_index'),
        ),
    ]
