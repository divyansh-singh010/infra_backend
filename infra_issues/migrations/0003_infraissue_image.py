# Generated by Django 5.0.1 on 2024-05-23 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infra_issues', '0002_rename_complex_infraissue_complex_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='infraissue',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='infra_issues/images/'),
        ),
    ]
