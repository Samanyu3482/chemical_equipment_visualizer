from django.db import models
from django.contrib.auth.models import User


class EquipmentUpload(models.Model):
    """Model to track CSV upload metadata"""
    filename = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    record_count = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_timestamp']
        
    def __str__(self):
        return f"{self.filename} ({self.record_count} records)"


class EquipmentRecord(models.Model):
    """Model to store individual equipment data records"""
    upload = models.ForeignKey(EquipmentUpload, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    class Meta:
        indexes = [
            models.Index(fields=['equipment_type']),
            models.Index(fields=['upload']),
        ]
        
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"