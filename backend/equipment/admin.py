from django.contrib import admin
from .models import EquipmentUpload, EquipmentRecord


@admin.register(EquipmentUpload)
class EquipmentUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'upload_timestamp', 'record_count', 'user']
    list_filter = ['upload_timestamp', 'user']
    readonly_fields = ['upload_timestamp']


@admin.register(EquipmentRecord)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'upload']
    list_filter = ['equipment_type', 'upload']
    search_fields = ['equipment_name', 'equipment_type']