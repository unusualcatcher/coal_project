# Generated by Django 5.1.1 on 2024-09-15 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coal', '0002_miningactivity_energy_grid_mix_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='miningactivity',
            name='carbon_emitted',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
