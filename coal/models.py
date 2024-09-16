from django.db import models

class MiningActivity(models.Model):
    date_of_activity = models.DateField()
    material_extracted = models.CharField(max_length=100)
    quantity_extracted = models.PositiveIntegerField()  # in tons
    energy_consumption = models.PositiveIntegerField()  # in kWh
    fuel_consumption = models.PositiveIntegerField()  # in liters
    energy_grid_mix = models.CharField(max_length=50, null=True)  # Allow null values
    fuel_type = models.CharField(max_length=50, null=True)  # Allow null values
    explosives_type = models.CharField(max_length=50, null=True)  # Allow null values
    total_explosives_used = models.PositiveIntegerField(null=True)  # Allow null values
    operational_hours = models.DurationField(null=True)  # Allow null values
    downtime_duration = models.DurationField(null=True)  # Allow null values
    production_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)  # Allow null values
    trucks_loaded = models.PositiveIntegerField(null=True)  # Allow null values
    distance_mined = models.PositiveIntegerField(null=True)  # Allow null values
    carbon_emitted = models.PositiveIntegerField(null=True) 

    def __str__(self):
        return f"Mining Activity on {self.date_of_activity}"


class Graph(models.Model):
    mining_activity = models.ForeignKey(MiningActivity, on_delete=models.CASCADE, related_name='graphs')
    image = models.ImageField(upload_to='graphs/')  # Stores the image locally

    def __str__(self):
        return f"Graph for Mining Activity on {self.mining_activity.date_of_activity}"
