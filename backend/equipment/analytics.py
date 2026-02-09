import pandas as pd
from typing import Dict, List, Any
from dataclasses import dataclass
from .models import EquipmentRecord, EquipmentUpload


@dataclass
class AnalyticsSummary:
    """Summary statistics for equipment data"""
    total_equipment: int
    average_flowrate: float
    average_pressure: float
    average_temperature: float
    type_distribution: Dict[str, int]


class AnalyticsEngine:
    """Handles analytics calculations for equipment data"""
    
    def calculate_averages(self, records: List[EquipmentRecord]) -> Dict[str, float]:
        """Calculate average values for numeric parameters"""
        if not records:
            return {
                'flowrate': 0.0,
                'pressure': 0.0,
                'temperature': 0.0
            }
        
        # Convert to DataFrame for efficient calculations
        data = {
            'flowrate': [record.flowrate for record in records],
            'pressure': [record.pressure for record in records],
            'temperature': [record.temperature for record in records]
        }
        df = pd.DataFrame(data)
        
        return {
            'flowrate': float(df['flowrate'].mean()),
            'pressure': float(df['pressure'].mean()),
            'temperature': float(df['temperature'].mean())
        }
    
    def analyze_type_distribution(self, records: List[EquipmentRecord]) -> Dict[str, int]:
        """Analyze equipment type distribution"""
        if not records:
            return {}
        
        # Count occurrences of each equipment type
        type_counts = {}
        for record in records:
            equipment_type = record.equipment_type
            type_counts[equipment_type] = type_counts.get(equipment_type, 0) + 1
        
        return type_counts
    
    def generate_summary_statistics(self, records: List[EquipmentRecord]) -> AnalyticsSummary:
        """Generate complete analytics summary"""
        total_count = len(records)
        averages = self.calculate_averages(records)
        type_distribution = self.analyze_type_distribution(records)
        
        return AnalyticsSummary(
            total_equipment=total_count,
            average_flowrate=averages['flowrate'],
            average_pressure=averages['pressure'],
            average_temperature=averages['temperature'],
            type_distribution=type_distribution
        )
    
    def get_latest_upload_summary(self) -> AnalyticsSummary:
        """Get analytics summary for the most recent upload"""
        try:
            latest_upload = EquipmentUpload.objects.latest('upload_timestamp')
            records = list(latest_upload.records.all())
            return self.generate_summary_statistics(records)
        except EquipmentUpload.DoesNotExist:
            # Return empty summary if no uploads exist
            return AnalyticsSummary(
                total_equipment=0,
                average_flowrate=0.0,
                average_pressure=0.0,
                average_temperature=0.0,
                type_distribution={}
            )
    
    def get_upload_summary(self, upload_id: int) -> AnalyticsSummary:
        """Get analytics summary for a specific upload"""
        try:
            upload = EquipmentUpload.objects.get(id=upload_id)
            records = list(upload.records.all())
            return self.generate_summary_statistics(records)
        except EquipmentUpload.DoesNotExist:
            raise ValueError(f"Upload with ID {upload_id} not found")
    
    def validate_summary_consistency(self, summary: AnalyticsSummary) -> bool:
        """Validate that summary statistics are consistent"""
        # Check that type distribution sum equals total equipment
        if summary.type_distribution:
            distribution_sum = sum(summary.type_distribution.values())
            if distribution_sum != summary.total_equipment:
                return False
        
        # Check that averages are reasonable (non-negative for our use case)
        if (summary.average_flowrate < 0 or 
            summary.average_pressure < 0 or 
            summary.average_temperature < -273):  # Absolute zero check
            return False
        
        return True