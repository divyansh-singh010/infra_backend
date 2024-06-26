# Generated by Django 5.0.1 on 2024-06-01 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InfraIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complex_name', models.CharField(max_length=100)),
                ('room', models.CharField(max_length=100)),
                ('issue', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]
