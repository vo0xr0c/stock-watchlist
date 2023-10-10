"""
casestudy REST URL Configuration.
"""
from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import include, path

from . import views

router = DefaultRouter()
router.register(r'securities', views.SecurityViewSet, basename='security')
router.register(r'watchlist', views.WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name='login'),
    path('api/', include(router.urls)),
]
