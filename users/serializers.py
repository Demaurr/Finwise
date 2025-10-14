from rest_framework import serializers
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    location = serializers.JSONField(required=False)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'password2', 'location']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = UserProfile(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'full_name', 'email', 'location',
            'date_joined', 'last_login', 'is_staff',
        ]
        read_only_fields = ['date_joined', 'last_login', 'is_staff']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

