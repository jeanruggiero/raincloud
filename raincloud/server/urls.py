from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data/<int:sensor_id>/', views.Data.as_view(), name='data'),
    path('sensors/', views.SensorList.as_view(), name='sensor_list'),
    path('sensors/<int:sensor_id>/', views.SensorDetail.as_view(), name='sensor_detail')
]
