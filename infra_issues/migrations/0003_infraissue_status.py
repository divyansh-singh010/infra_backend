# Generated by Django 5.0.1 on 2024-06-09 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infra_issues', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='infraissue',
            name='status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]
