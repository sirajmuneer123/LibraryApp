#import restframework modles
from rest_framework.pagination import  PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    SAFE_METHODS
)

from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

# import django exception modules and datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import datetime


#import model classes
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from Api.models import Book, Order, TimePeriod
from django.contrib.auth.models import Permission


# import serializers class
from Api.serializers import (
    UserSerializer,
    BookSerializer,
    OrderSerializer,
    PermissionSerializer
)


class Login(APIView):
    """ login api for all user types (admin, staff, user)
    """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'status': 'failed','error': 'Please provide both username and password'},
                            status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'status': 'failed','error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        elif django_user.groups.filter(name = 'user').exists():
            try:
                set_time = TimePeriod.objects.last()
                if not set_time.start_time <= datetime.datetime.now().time() < set_time.end_time:
                    return Response({'status': 'failed', 'error': 'Not valid time to add user'}) 
            except ObjectDoesNotExist:
                return Response({'status': 'failed', 'error': 'Please Set time period'})

        serializer = UserSerializer(user)
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'token': token, 'data': serializer.data},
                        status=HTTP_200_OK)




class UserPermission(BasePermission):
    """
        create user by admin and checking permission 
    """
    def has_permission(self, request, view):
        group =request.user.groups.values_list('name', flat=True)[0]
        return group == 'admin'

class CreateUserView(APIView):
    """ create all user types using this api like admin, staff and user
    """

    permission_classes = (IsAuthenticated, UserPermission,)

    def put(self, request, pk, format=None):
        data = request.data
        user_obj.first_name = data.get('first_name', user_obj.first_name)
        user_obj.last_name = data.get('last_name', user_obj.last_name)
        user_obj.email = data.get('email', user_obj.email)
        return Response({'status': 'success'})
    

    def get(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response({'status': 'success', 'data': serializer.data})
        except ObjectDoesNotExist:
            return Response({'status': 'failed','error': 'Object does not exist'},
                            status=HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        with transaction.atomic():
            user_data = request.data
            group_name = user_data.get('group')
            if group_name == 'user':
                try:
                    set_time = TimePeriod.objects.last()
                    if not set_time.start_time <= datetime.datetime.now().time() < set_time.end_time:
                       return Response({'status': 'failed', 'error': 'Not valid time to add user'}) 
                except ObjectDoesNotExist:
                    return Response({'status': 'failed', 'error': 'Please Set time period'})
            if User.objects.filter(username=user_data.get('username')).exists():
                return Response({'status': 'failed', 'error': 'username already exists'})
            else:
                user_obj = User.objects.create_user(
                    username = user_data.get('username'),
                    first_name = user_data.get('first_name'),
                    last_name = user_data.get('last_name'),
                    email = user_data.get('email'),
                    password=user_data.get('password')
                )
                group_name = user_data.get('group')
                if group_name:
                    grp, created = Group.objects.get_or_create(
                        name=group_name)
                    user_obj.groups.add(g)
                    
            return Response({'status': 'success', 'msg': 'User Created Successfully'})


class BookPermission(BasePermission):
    def has_permission(self, request, view):
        group =request.user.groups.values_list('name', flat=True)[0]
        valid_staff = request.user.has_perm('Api.staff_add_book')
        if group == 'staff' and request.method == 'POST':
            return valid_staff
        else:
            return group == 'admin'

class BookCreate(generics.CreateAPIView):
    """ To crate book, both admin and staff can add book
        with permission 
    """
    permission_classes = (IsAuthenticated, BookPermission)
    serializer_class = BookSerializer

class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    """ Get, update and delete book using this api
    """
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated, BookPermission)

    def get_queryset(self):
        return Book.objects.filter(id=self.kwargs['pk'])


class PermissionListView(ListAPIView):
    """ this api will return all permisson for staff user
    """
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Permission.objects.filter(codename__startswith='staff')


class OrderCreate(APIView):
    """ Create actual user for the system
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        with transaction.atomic():
            order_data = request.data
            book = Book.objects.filter(book_id=order_data.get('book_id'))
            if book.available_copies > 0:
                return Response({'status': 'error', 'error': 'This book is not available'})
            else:
                order_obj = Order.objects.create(
                    customer_id = order_data.get('customer_id'),
                    book_id = order_data.get('book_id'),
                    issue_date = order_data.get('issue_date'),
                    return_date = order_data.get('return_date'),
                    status=order_data.get('status')
                )
                book.available_copies = book.available_copies - 1
                book.save()      
            return Response({'status': 'success', 'msg': 'successfully requested'})



class AddPermission(APIView):
    """ add permission for staff to grant add new books into the system
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        data = request.data
        permission = Permission.objects.get(id=data.get('permission_id'))
        user = User.objects.get(id=data.get('user_id')) 
        user.user_permissions.add(Permission)
        return Response({'status': 'success', 'msg': 'successfully added'})


class PagesPagination(PageNumberPagination):
    """ To set default book list pagination size
    """
    page_size = 10

class BookListAPIView(generics.ListAPIView):
    """ To get 10 books at a time and we can paginate over it
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookSerializer
    pagination_class = PagesPagination
    
    def get_queryset(self):
        return Book.objects.all()





# Using the standard RequestFactory API to create a form POST request
from rest_framework.test import APIRequestFactory


factory = APIRequestFactory()
request = factory.post('/api/book-create/', {
    "title":"klda", "author": "book", "book_code": "sdfddsd",
    "total_copies" :"7", "available_copies":"3"}, format='json')
print("test rsult", request)