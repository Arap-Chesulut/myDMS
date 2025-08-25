from django.contrib import admin
from .models import Region, EnvironmentalData, DataUpload

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'risk_level', 'area_sq_km', 'population']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['name', 'code']

@admin.register(EnvironmentalData)
class EnvironmentalDataAdmin(admin.ModelAdmin):
    list_display = ['region', 'date', 'vegetation_index', 'land_degradation_index', 'source']
    list_filter = ['region', 'source', 'date']
    search_fields = ['region__name']

@admin.register(DataUpload)
class DataUploadAdmin(admin.ModelAdmin):
    list_display = ['region', 'file_type', 'status', 'uploaded_by', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    readonly_fields = ['processed_records', 'total_records', 'errors', 'created_at', 'completed_at']