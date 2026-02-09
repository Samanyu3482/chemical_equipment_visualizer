import pandas as pd
import io
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from django.core.exceptions import ValidationError


@dataclass
class ValidationResult:
    """Result of CSV validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class EquipmentData:
    """Parsed equipment data record"""
    equipment_name: str
    equipment_type: str
    flowrate: float
    pressure: float
    temperature: float


class CSVProcessor:
    """Handles CSV file validation and parsing for equipment data"""
    
    REQUIRED_COLUMNS = [
        'Equipment Name',
        'Type',
        'Flowrate',
        'Pressure',
        'Temperature'
    ]
    
    NUMERIC_COLUMNS = ['Flowrate', 'Pressure', 'Temperature']
    
    # Data constraints
    CONSTRAINTS = {
        'Flowrate': {'min': 0, 'max': 10000},
        'Pressure': {'min': 0, 'max': 1000},
        'Temperature': {'min': -273, 'max': 1000}
    }
    
    def validate_structure(self, csv_file) -> ValidationResult:
        """Validate CSV file structure and column headers"""
        errors = []
        warnings = []
        
        try:
            # Reset file pointer
            csv_file.seek(0)
            
            # Read CSV with pandas
            df = pd.read_csv(csv_file)
            
            # Check if file is empty
            if df.empty:
                errors.append("CSV file is empty")
                return ValidationResult(False, errors, warnings)
            
            # Check column headers
            actual_columns = df.columns.tolist()
            
            # Check for exact column match
            if actual_columns != self.REQUIRED_COLUMNS:
                missing_cols = set(self.REQUIRED_COLUMNS) - set(actual_columns)
                extra_cols = set(actual_columns) - set(self.REQUIRED_COLUMNS)
                
                if missing_cols:
                    errors.append(f"Missing required columns: {', '.join(missing_cols)}")
                
                if extra_cols:
                    warnings.append(f"Extra columns found (will be ignored): {', '.join(extra_cols)}")
                
                # Check if columns are in wrong order
                if set(actual_columns) == set(self.REQUIRED_COLUMNS):
                    errors.append(f"Columns are in wrong order. Expected: {', '.join(self.REQUIRED_COLUMNS)}")
            
            # Check for minimum number of data rows
            if len(df) == 0:
                errors.append("No data rows found in CSV file")
            
            return ValidationResult(len(errors) == 0, errors, warnings)
            
        except pd.errors.EmptyDataError:
            errors.append("CSV file is empty or contains no data")
        except pd.errors.ParserError as e:
            errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error reading CSV: {str(e)}")
        
        return ValidationResult(False, errors, warnings)
    
    def validate_data_types(self, df: pd.DataFrame) -> ValidationResult:
        """Validate data types and constraints for numeric columns"""
        errors = []
        warnings = []
        
        # Check numeric columns
        for col in self.NUMERIC_COLUMNS:
            if col not in df.columns:
                continue
                
            # Check for empty strings first
            empty_string_mask = df[col].astype(str).str.strip() == ''
            
            # Check for non-numeric values (excluding already empty strings)
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            non_numeric_mask = numeric_series.isna() & ~empty_string_mask
            
            invalid_mask = non_numeric_mask | empty_string_mask
            
            if invalid_mask.any():
                invalid_rows = df.index[invalid_mask].tolist()
                invalid_values = df.loc[invalid_mask, col].tolist()
                errors.append(
                    f"Non-numeric values in column '{col}' at rows {invalid_rows}: {invalid_values}"
                )
                continue
            
            # Check constraints
            if col in self.CONSTRAINTS:
                constraints = self.CONSTRAINTS[col]
                min_val, max_val = constraints['min'], constraints['max']
                
                # Check minimum values
                below_min = numeric_series < min_val
                if below_min.any():
                    invalid_rows = df.index[below_min].tolist()
                    errors.append(
                        f"Values in column '{col}' below minimum ({min_val}) at rows {invalid_rows}"
                    )
                
                # Check maximum values
                above_max = numeric_series > max_val
                if above_max.any():
                    invalid_rows = df.index[above_max].tolist()
                    errors.append(
                        f"Values in column '{col}' above maximum ({max_val}) at rows {invalid_rows}"
                    )
        
        # Check for empty string values in required text columns
        text_columns = ['Equipment Name', 'Type']
        for col in text_columns:
            if col in df.columns:
                empty_mask = df[col].astype(str).str.strip() == ''
                if empty_mask.any():
                    invalid_rows = df.index[empty_mask].tolist()
                    errors.append(f"Empty values in column '{col}' at rows {invalid_rows}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def parse_equipment_data(self, csv_file) -> Tuple[List[EquipmentData], ValidationResult]:
        """Parse CSV file and return list of EquipmentData objects"""
        # First validate structure
        structure_result = self.validate_structure(csv_file)
        if not structure_result.is_valid:
            return [], structure_result
        
        try:
            # Reset file pointer and read CSV
            csv_file.seek(0)
            df = pd.read_csv(csv_file)
            
            # Filter to only required columns in correct order
            df = df[self.REQUIRED_COLUMNS]
            
            # Validate data types
            data_result = self.validate_data_types(df)
            if not data_result.is_valid:
                return [], data_result
            
            # Convert to EquipmentData objects
            equipment_records = []
            for _, row in df.iterrows():
                equipment_data = EquipmentData(
                    equipment_name=str(row['Equipment Name']).strip(),
                    equipment_type=str(row['Type']).strip(),
                    flowrate=float(row['Flowrate']),
                    pressure=float(row['Pressure']),
                    temperature=float(row['Temperature'])
                )
                equipment_records.append(equipment_data)
            
            # Combine warnings from structure and data validation
            all_warnings = structure_result.warnings + data_result.warnings
            success_result = ValidationResult(True, [], all_warnings)
            
            return equipment_records, success_result
            
        except Exception as e:
            error_result = ValidationResult(False, [f"Error parsing CSV data: {str(e)}"])
            return [], error_result
    
    def get_sample_csv_content(self) -> str:
        """Generate sample CSV content for demonstration"""
        sample_data = [
            ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'],
            ['Pump-1', 'Pump', '120.5', '5.6', '60.0'],
            ['Valve-3', 'Valve', '80.0', '3.2', '45.0'],
            ['Reactor-A', 'Reactor', '200.0', '10.1', '350.0'],
            ['Heat-Exchanger-1', 'Heat Exchanger', '150.0', '7.8', '120.0'],
            ['Compressor-2', 'Compressor', '300.0', '15.2', '85.0']
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        for row in sample_data:
            output.write(','.join(row) + '\n')
        
        return output.getvalue()