# Generated by Django 5.1.2 on 2024-10-18 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_contact_city_contact_state_contact_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
    ]