from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import auth_views

urlpatterns = [
    # Authentication endpoints
    path('login/', auth_views.login_user, name='auth_login'),
    path('register/', auth_views.register_user, name='auth_register'),
    path('logout/', auth_views.logout_user, name='auth_logout'),
    path('verify/', auth_views.verify_token, name='auth_verify'),
    path('profile/', auth_views.user_profile, name='auth_profile'),
    
    # JWT token endpoints
    path('token/', auth_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]