from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data/<int:sensor_id>/', views.Data.as_view(), name='data')
]
