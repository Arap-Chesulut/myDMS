from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, StdDev, Count
from django.utils import timezone
from datetime import timedelta
from .models import AnalysisReport, RiskPrediction
from .serializers import (
    AnalysisReportSerializer, RiskPredictionSerializer,
    ReportRequestSerializer, PredictionRequestSerializer
)
from apps.monitoring.models import EnvironmentalData

class AnalysisReportViewSet(viewsets.ModelViewSet):
    queryset = AnalysisReport.objects.all()
    serializer_class = AnalysisReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return AnalysisReport.objects.all()
        return AnalysisReport.objects.filter(generated_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = ReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Here you would implement the actual report generation logic
        # For now, we'll just create a placeholder report
        from apps.monitoring.models import Region
        
        try:
            region = Region.objects.get(id=serializer.validated_data['region_id'])
            
            report = AnalysisReport.objects.create(
                title=f"{serializer.validated_data['report_type']} Report for {region.name}",
                report_type=serializer.validated_data['report_type'],
                region=region,
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                format=serializer.validated_data['format'],
                generated_by=request.user,
                parameters=serializer.validated_data.get('parameters', {})
            )
            
            return Response(AnalysisReportSerializer(report).data)
            
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)

class RiskPredictionViewSet(viewsets.ModelViewSet):
    queryset = RiskPrediction.objects.all()
    serializer_class = RiskPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        serializer = PredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Simple risk prediction algorithm (placeholder)
        data = serializer.validated_data
        
        # Basic risk calculation based on environmental factors
        risk_score = (
            (1 - data['vegetation_index']) * 0.4 +
            (1 - data['soil_moisture'] / 100) * 0.3 +
            (1 - min(data['rainfall'] / 100, 1)) * 0.2 +
            (data['temperature'] / 50) * 0.1
        )
        
        risk_score = max(0, min(1, risk_score))  # Clamp between 0 and 1
        
        from apps.monitoring.models import Region
        
        try:
            region = Region.objects.get(id=data['region_id'])
            
            prediction = RiskPrediction.objects.create(
                region=region,
                prediction_date=timezone.now().date(),
                risk_score=risk_score,
                confidence=0.85,  # Placeholder confidence
                factors={
                    'vegetation_impact': (1 - data['vegetation_index']) * 0.4,
                    'soil_moisture_impact': (1 - data['soil_moisture'] / 100) * 0.3,
                    'rainfall_impact': (1 - min(data['rainfall'] / 100, 1)) * 0.2,
                    'temperature_impact': (data['temperature'] / 50) * 0.1
                }
            )
            
            return Response(RiskPredictionSerializer(prediction).data)
            
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)

class DashboardView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Get basic statistics for dashboard
        total_regions = Region.objects.count()
        total_data_points = EnvironmentalData.objects.count()
        latest_data = EnvironmentalData.objects.order_by('-timestamp').first()
        
        # Calculate average risk across regions
        regions_with_data = Region.objects.filter(environmental_data__isnull=False).distinct()
        avg_risk = EnvironmentalData.objects.aggregate(
            avg_risk=Avg('land_degradation_index')
        )['avg_risk'] or 0
        
        return Response({
            'total_regions': total_regions,
            'total_data_points': total_data_points,
            'average_risk': avg_risk,
            'latest_data_date': latest_data.date if latest_data else None,
            'high_risk_regions': regions_with_data.filter(
                environmental_data__land_degradation_index__gt=0.7
            ).count()
        })