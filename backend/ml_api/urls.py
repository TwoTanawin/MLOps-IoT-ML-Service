from django.urls import path
from .views import ClassifySensorData, GetLatestResult

urlpatterns = [
    path('classification-data/', ClassifySensorData.as_view(), name='classification-data'),
    path('get-result/', GetLatestResult.as_view(), name='get-result'),
]