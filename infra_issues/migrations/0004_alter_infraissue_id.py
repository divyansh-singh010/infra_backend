# Generated by Django 5.0.1 on 2024-06-09 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infra_issues', '0003_infraissue_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infraissue',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
