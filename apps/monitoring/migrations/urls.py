from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'environmental-data', views.EnvironmentalDataViewSet)
router.register(r'data-uploads', views.DataUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]