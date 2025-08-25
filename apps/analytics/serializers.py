from rest_framework import serializers
from .models import AnalysisReport, RiskPrediction

class AnalysisReportSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = AnalysisReport
        fields = '__all__'
        read_only_fields = ['generated_by', 'generated_at', 'file']

class RiskPredictionSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = RiskPrediction
        fields = '__all__'

class ReportRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=AnalysisReport.REPORT_TYPES)
    region_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    format = serializers.ChoiceField(choices=AnalysisReport.FORMAT_CHOICES, default='pdf')
    parameters = serializers.JSONField(required=False, default=dict)

class PredictionRequestSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    vegetation_index = serializers.FloatField(required=True)
    soil_moisture = serializers.FloatField(required=True)
    rainfall = serializers.FloatField(required=True)
    temperature = serializers.FloatField(required=False, default=25.0)
    wind_speed = serializers.FloatField(required=False, default=0.0)