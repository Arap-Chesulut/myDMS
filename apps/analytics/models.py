from django.db import models
from apps.monitoring.models import Region
from apps.users.models import User

class AnalysisReport(models.Model):
    REPORT_TYPES = (
        ('risk_assessment', 'Risk Assessment'),
        ('trend_analysis', 'Trend Analysis'),
        ('comparative', 'Comparative Analysis'),
        ('prediction', 'Prediction Report'),
    )
    
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    )
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    parameters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.region}"

class RiskPrediction(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    prediction_date = models.DateField()
    risk_score = models.FloatField(help_text="Predicted risk score (0-1)")
    confidence = models.FloatField(help_text="Prediction confidence (0-1)")
    factors = models.JSONField(default=dict, help_text="Factors contributing to the prediction")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-prediction_date']
        unique_together = ['region', 'prediction_date']
    
    def __str__(self):
        return f"Risk Prediction - {self.region} ({self.prediction_date})"