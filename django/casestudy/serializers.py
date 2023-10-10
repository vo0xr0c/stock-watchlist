"""
Serializers for the models in the casestudy app
"""
from rest_framework import serializers

from .models import Security, User


class SecuritySerializer(serializers.ModelSerializer):
    """
    Serializer for the Security model.
    Fields: id, ticker, name, last_price, last_updated
    """
    class Meta:
        model = Security
        fields = ['id', 'ticker', 'name', 'last_price', 'last_updated']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Fields: id, username, email, first_name, last_name
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
