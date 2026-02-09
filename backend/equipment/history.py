from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from django.db import transaction
from .models import EquipmentUpload, EquipmentRecord


@dataclass
class HistoryEntry:
    """Metadata for an upload in history"""
    upload_id: int
    filename: str
    timestamp: datetime
    record_count: int


class HistoryManager:
    """Manages upload history with 5-record limit"""
    
    MAX_HISTORY_RECORDS = 5
    
    def add_upload(self, filename: str, record_count: int, user=None) -> EquipmentUpload:
        """Add a new upload and maintain history limit"""
        with transaction.atomic():
            # Create new upload record
            upload = EquipmentUpload.objects.create(
                filename=filename,
                record_count=record_count,
                user=user
            )
            
            # Enforce 5-record limit
            self._enforce_history_limit()
            
            return upload
    
    def _enforce_history_limit(self):
        """Remove oldest records if we exceed the limit"""
        total_uploads = EquipmentUpload.objects.count()
        
        if total_uploads > self.MAX_HISTORY_RECORDS:
            # Get uploads to delete (oldest first)
            excess_count = total_uploads - self.MAX_HISTORY_RECORDS
            oldest_uploads = EquipmentUpload.objects.order_by('upload_timestamp')[:excess_count]
            
            # Delete the oldest uploads (this will cascade to related records)
            for upload in oldest_uploads:
                upload.delete()
    
    def get_history(self) -> List[HistoryEntry]:
        """Get upload history in reverse chronological order (newest first)"""
        uploads = EquipmentUpload.objects.order_by('-upload_timestamp')[:self.MAX_HISTORY_RECORDS]
        
        history_entries = []
        for upload in uploads:
            entry = HistoryEntry(
                upload_id=upload.id,
                filename=upload.filename,
                timestamp=upload.upload_timestamp,
                record_count=upload.record_count
            )
            history_entries.append(entry)
        
        return history_entries
    
    def get_history_metadata(self) -> List[Dict[str, Any]]:
        """Get history metadata as dictionaries for API serialization"""
        history_entries = self.get_history()
        
        metadata_list = []
        for entry in history_entries:
            metadata = {
                'upload_id': entry.upload_id,
                'filename': entry.filename,
                'timestamp': entry.timestamp.isoformat(),
                'record_count': entry.record_count
            }
            metadata_list.append(metadata)
        
        return metadata_list
    
    def get_upload_by_id(self, upload_id: int) -> EquipmentUpload:
        """Get a specific upload by ID"""
        try:
            return EquipmentUpload.objects.get(id=upload_id)
        except EquipmentUpload.DoesNotExist:
            raise ValueError(f"Upload with ID {upload_id} not found")
    
    def get_current_history_count(self) -> int:
        """Get the current number of uploads in history"""
        return EquipmentUpload.objects.count()
    
    def clear_history(self):
        """Clear all upload history (for testing purposes)"""
        EquipmentUpload.objects.all().delete()
    
    def validate_history_limit(self) -> bool:
        """Validate that history doesn't exceed the limit"""
        return self.get_current_history_count() <= self.MAX_HISTORY_RECORDS