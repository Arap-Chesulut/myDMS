from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Region, EnvironmentalData, DataUpload

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class EnvironmentalDataSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = EnvironmentalData
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'timestamp']
    
    def create(self, validated_data):
        # Extract latitude/longitude and create Point
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        validated_data['location'] = Point(longitude, latitude)
        
        # Set uploaded_by from request user
        validated_data['uploaded_by'] = self.context['request'].user
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add coordinates to representation
        representation['latitude'] = instance.location.y
        representation['longitude'] = instance.location.x
        return representation

class BoundingBoxSerializer(serializers.Serializer):
    sw_lat = serializers.FloatField(required=True)
    sw_lng = serializers.FloatField(required=True)
    ne_lat = serializers.FloatField(required=True)
    ne_lng = serializers.FloatField(required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    sources = serializers.ListField(
        child=serializers.ChoiceField(choices=EnvironmentalData.SOURCE_CHOICES),
        required=False
    )

class DataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUpload
        fields = '__all__'
        read_only_fields = ['status', 'processed_records', 'total_records', 
                           'errors', 'uploaded_by', 'created_at', 'completed_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)