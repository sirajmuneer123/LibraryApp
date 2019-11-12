
from rest_framework.serializers import (
    ModelSerializer, PrimaryKeyRelatedField,
    SerializerMethodField
)
from Api.models import Book, Order
from django.contrib.auth.models import User, Permission

class PermissionSerializer(ModelSerializer):
    """ Serializer for Permission
    """
    class Meta:
        model = Permission
        fields = '__all__'

class UserSerializer(ModelSerializer):
    """ serializer for User
    """
    class Meta:
        model = User
        exclude = ['password']



class BookSerializer(ModelSerializer):
    """ serializer for book
    """
    class Meta:
        model = Book
        fields = '__all__'



class OrderSerializer(ModelSerializer):
    """ Serializer for request book
    """
    class Meta:
        model = Order
        fields = '__all__'