from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Apps
    path('api/journal/', include('apps.journal.urls')),
    path('api/meals/', include('apps.food.urls')),
    path('api/whoop/', include('apps.health.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
