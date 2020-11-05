# Generated by Django 3.1.2 on 2020-11-01 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_user_information'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='information',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.information'),
        ),
    ]