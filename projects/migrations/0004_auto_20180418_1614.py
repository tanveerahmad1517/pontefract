# Generated by Django 2.0.2 on 2018-04-18 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20180418_1317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='session',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='session',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='session',
            name='start_time',
        ),
    ]
