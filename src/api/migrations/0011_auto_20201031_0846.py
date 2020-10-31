# Generated by Django 3.1.2 on 2020-10-31 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20201029_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Information',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('token_id', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=254)),
                ('scheduled_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.scheduleddate')),
            ],
        ),
        migrations.DeleteModel(
            name='Name',
        ),
    ]
