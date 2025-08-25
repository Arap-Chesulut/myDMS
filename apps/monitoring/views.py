from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Polygon
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from .models import Region, EnvironmentalData, DataUpload
from .serializers import (
    RegionSerializer, EnvironmentalDataSerializer, 
    BoundingBoxSerializer, DataUploadSerializer
)

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        region = self.get_object()
        time_range = request.query_params.get('time_range', '30d')
        
        # Calculate time range
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == '30d':
            start_date = timezone.now() - timedelta(days=30)
        elif time_range == '1y':
            start_date = timezone.now() - timedelta(days=365)
        else:
            start_date = None
        
        queryset = EnvironmentalData.objects.filter(region=region)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        stats = queryset.aggregate(
            data_points=Count('id'),
            avg_vegetation=Avg('vegetation_index'),
            avg_soil_moisture=Avg('soil_moisture'),
            avg_rainfall=Avg('rainfall'),
            avg_degradation=Avg('land_degradation_index'),
            max_degradation=Max('land_degradation_index'),
            min_degradation=Min('land_degradation_index'),
        )
        
        return Response(stats)

class EnvironmentalDataViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentalData.objects.all()
    serializer_class = EnvironmentalDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['region', 'date', 'source', 'quality_score']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by time range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def within_bbox(self, request):
        serializer = BoundingBoxSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        bbox = Polygon.from_bbox((
            data['sw_lng'], data['sw_lat'],
            data['ne_lng'], data['ne_lat']
        ))
        
        queryset = EnvironmentalData.objects.filter(location__within=bbox)
        
        # Apply additional filters
        if data.get('start_date'):
            queryset = queryset.filter(date__gte=data['start_date'])
        if data.get('end_date'):
            queryset = queryset.filter(date__lte=data['end_date'])
        if data.get('sources'):
            queryset = queryset.filter(source__in=data['sources'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        # Get latest data for each region
        regions = Region.objects.all()
        latest_data = []
        
        for region in regions:
            data = EnvironmentalData.objects.filter(region=region).order_by('-timestamp').first()
            if data:
                latest_data.append(data)
        
        serializer = self.get_serializer(latest_data, many=True)
        return Response(serializer.data)

class DataUploadViewSet(viewsets.ModelViewSet):
    queryset = DataUpload.objects.all()
    serializer_class = DataUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return DataUpload.objects.all()
        return DataUpload.objects.filter(uploaded_by=self.request.user)
    
    def perform_create(self, serializer):
        upload = serializer.save()
        # Start async processing (we'll implement this later)
        # process_data_upload.delay(upload.id)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        upload = self.get_object()
        return Response({
            'status': upload.status,
            'processed': upload.processed_records,
            'total': upload.total_records,
            'errors': upload.errors
        })