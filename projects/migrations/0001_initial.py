# Generated by Django 2.0.2 on 2018-04-26 16:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.base
import timezone_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projects',
                'ordering': [django.db.models.functions.base.Lower('name')],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('timezone', timezone_field.fields.TimeZoneField()),
                ('breaks', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project')),
            ],
            options={
                'db_table': 'sessions',
            },
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together={('name', 'user')},
        ),
    ]
