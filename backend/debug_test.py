import io
from equipment.csv_processor import CSVProcessor

processor = CSVProcessor()

# Test with empty string
csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature\nEquipment-0,Pump,,,"
csv_file = io.StringIO(csv_content)

equipment_records, result = processor.parse_equipment_data(csv_file)

print(f"Result valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Records: {len(equipment_records)}")