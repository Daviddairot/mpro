# Generated by Django 5.0.6 on 2024-06-24 19:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapp', '0003_assessment_total'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='assessor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student',
            name='instrument',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='student',
            name='matric_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('ca', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('extra', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mapp.student')),
            ],
        ),
    ]
