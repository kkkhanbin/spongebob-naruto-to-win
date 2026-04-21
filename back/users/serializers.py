from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'birth_date', 'is_verified']
        read_only_fields = ['id', 'username', 'email', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'password']

    def to_internal_value(self, data):
        mutable_data = data.copy()
        if mutable_data.get('birth_date') == '':
            mutable_data['birth_date'] = None
        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
