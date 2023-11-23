
from django.urls import path,include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from accounts import views


router = routers.DefaultRouter()
router.register(r'user-register', views.RegisterView, basename='task')


urlpatterns = [ 
    path('',include(router.urls)),
    path('api/',include('accounts.urls')),
    
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)