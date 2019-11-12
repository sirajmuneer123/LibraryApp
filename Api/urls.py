from django.urls import path
from Api.views import (
    Login, CreateUserView, BookCreate,
    BookDetails, OrderCreate, PermissionListView,
    AddPermission, BookListAPIView
)
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('login', Login.as_view(), name='login'),
    path('user/<pk>/', CreateUserView.as_view(), name='user-data'),
    path('user-create/', CreateUserView.as_view(), name='user-create'),
    path('book-create/', BookCreate.as_view(), name='book-create'),
    path('book-details/<pk>/', BookDetails.as_view(), name='book-details'),
    path('order-create/', OrderCreate.as_view(), name='order-create'),
    path('permission-list/', PermissionListView.as_view(), name='permission-list'),
    path('permission-add/', AddPermission.as_view(), name='permission-add'),
    path('book-list/', BookListAPIView.as_view(), name='book-list'),
]