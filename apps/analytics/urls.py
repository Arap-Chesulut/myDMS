from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.AnalysisReportViewSet)
router.register(r'predictions', views.RiskPredictionViewSet)
router.register(r'dashboard', views.DashboardView, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]