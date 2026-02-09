import io
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EquipmentUpload, EquipmentRecord
from .csv_processor import CSVProcessor
from .analytics import AnalyticsEngine
from .history import HistoryManager
from .report_generator import ReportGenerator
from .serializers import (
    AnalyticsSummarySerializer, HistoryEntrySerializer, 
    ErrorResponseSerializer, UploadResponseSerializer,
    EquipmentUploadSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    Upload and process CSV file
    POST /api/upload/
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process CSV file
        processor = CSVProcessor()
        history_manager = HistoryManager()
        
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_file = io.StringIO(file_content)
        
        # Parse and validate CSV
        equipment_data, validation_result = processor.parse_equipment_data(csv_file)
        
        if not validation_result.is_valid:
            serializer = UploadResponseSerializer({
                'success': False,
                'errors': validation_result.errors
            })
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        # Save to database
        with transaction.atomic():
            # Create upload record
            upload = history_manager.add_upload(
                filename=uploaded_file.name,
                record_count=len(equipment_data),
                user=request.user
            )
            
            # Create equipment records
            equipment_records = []
            for data in equipment_data:
                record = EquipmentRecord(
                    upload=upload,
                    equipment_name=data.equipment_name,
                    equipment_type=data.equipment_type,
                    flowrate=data.flowrate,
                    pressure=data.pressure,
                    temperature=data.temperature
                )
                equipment_records.append(record)
            
            EquipmentRecord.objects.bulk_create(equipment_records)
        
        # Return success response
        response_data = {
            'success': True,
            'upload_id': upload.id,
            'record_count': len(equipment_data)
        }
        
        if validation_result.warnings:
            response_data['warnings'] = validation_result.warnings
        
        serializer = UploadResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request):
    """
    Get analytics summary for the latest upload
    GET /api/summary/
    """
    try:
        analytics = AnalyticsEngine()
        summary = analytics.get_latest_upload_summary()
        
        serializer = AnalyticsSummarySerializer(summary)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Error generating summary: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """
    Get upload history (last 5 uploads)
    GET /api/history/
    """
    try:
        history_manager = HistoryManager()
        history_entries = history_manager.get_history()
        
        serializer = HistoryEntrySerializer(history_entries, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Error retrieving history: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request):
    """
    Generate and download PDF report
    GET /api/report/pdf/
    """
    try:
        # Get optional upload_id parameter
        upload_id = request.GET.get('upload_id')
        include_charts = request.GET.get('include_charts', 'true').lower() == 'true'
        
        # Generate PDF report
        report_generator = ReportGenerator()
        
        try:
            pdf_data = report_generator.generate_report(
                upload_id=int(upload_id) if upload_id else None,
                include_charts=include_charts
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_data, content_type='application/pdf')
        
        # Set filename
        filename = f"equipment_report_{upload_id or 'latest'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_data)
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Error generating PDF report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_sample_csv(request):
    """
    Get sample CSV content for demonstration
    GET /api/sample-csv/
    """
    try:
        processor = CSVProcessor()
        sample_content = processor.get_sample_csv_content()
        
        response = HttpResponse(sample_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_equipment_data.csv"'
        return response
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Error generating sample CSV: {str(e)}'},
            status=500
        )