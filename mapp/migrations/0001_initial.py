# Generated by Django 5.0.6 on 2024-06-24 17:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_number', models.CharField(max_length=10, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('instrument', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song1', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('song2', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('song3', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('dressing', models.DecimalField(decimal_places=2, default=0.0, max_digits=4)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mapp.student')),
            ],
        ),
    ]
