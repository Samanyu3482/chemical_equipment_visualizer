from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import EquipmentUpload, EquipmentRecord


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']
        
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_username(self, value):
        """Validate username uniqueness"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class EquipmentRecordSerializer(serializers.ModelSerializer):
    """Serializer for equipment record data"""
    
    class Meta:
        model = EquipmentRecord
        fields = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class EquipmentUploadSerializer(serializers.ModelSerializer):
    """Serializer for equipment upload metadata"""
    records = EquipmentRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = EquipmentUpload
        fields = ['id', 'filename', 'upload_timestamp', 'record_count', 'records']


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary data"""
    total_equipment = serializers.IntegerField()
    average_flowrate = serializers.FloatField()
    average_pressure = serializers.FloatField()
    average_temperature = serializers.FloatField()
    type_distribution = serializers.DictField()


class HistoryEntrySerializer(serializers.Serializer):
    """Serializer for history entry metadata"""
    upload_id = serializers.IntegerField()
    filename = serializers.CharField()
    timestamp = serializers.DateTimeField()
    record_count = serializers.IntegerField()


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    error = serializers.CharField()
    details = serializers.ListField(child=serializers.CharField(), required=False)


class UploadResponseSerializer(serializers.Serializer):
    """Serializer for upload response"""
    success = serializers.BooleanField()
    upload_id = serializers.IntegerField(required=False)
    record_count = serializers.IntegerField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)