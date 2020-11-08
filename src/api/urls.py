from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api import views


router = DefaultRouter()
router.register(r'register', views.RegisterViewSet, basename='register')
router.register(r'api', views.ScheduleApiViewSet, basename='api')
router.register(r'calls', views.ApiCallsViewSet, basename='calls')


urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
]
