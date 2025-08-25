from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils import timezone
from apps.users.models import User

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    boundary = models.PolygonField(blank=True, null=True)
    area_sq_km = models.FloatField(blank=True, null=True)
    population = models.IntegerField(blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True)
    last_assessment = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EnvironmentalData(models.Model):
    SOURCE_CHOICES = (
        ('satellite', 'Satellite Imagery'),
        ('ground', 'Ground Measurement'),
        ('model', 'Model Prediction'),
    )
    
    location = models.PointField(geography=True)
    vegetation_index = models.FloatField(help_text="Normalized Difference Vegetation Index (NDVI)")
    soil_moisture = models.FloatField(help_text="Soil moisture content (%)")
    rainfall = models.FloatField(help_text="Rainfall in mm")
    land_degradation_index = models.FloatField(help_text="0-1 scale, higher means more degraded")
    temperature = models.FloatField(blank=True, null=True, help_text="Temperature in Celsius")
    wind_speed = models.FloatField(blank=True, null=True, help_text="Wind speed in m/s")
    humidity = models.FloatField(blank=True, null=True, help_text="Relative humidity (%)")
    date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='environmental_data')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    quality_score = models.FloatField(default=1.0, help_text="Data quality score 0-1")
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['region']),
            models.Index(fields=['source']),
        ]
        unique_together = ['location', 'timestamp', 'source']
    
    def __str__(self):
        return f"{self.region} - {self.date} (Deg: {self.land_degradation_index:.2f})"
    
    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

class DataUpload(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    file = models.FileField(upload_to='data_uploads/')
    file_type = models.CharField(max_length=10, choices=(('csv', 'CSV'), ('geojson', 'GeoJSON')))
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_records = models.IntegerField(default=0)
    total_records = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Upload {self.id} - {self.region} ({self.status})"