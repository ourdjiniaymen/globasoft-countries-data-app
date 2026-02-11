from django.urls import path
from . import views

app_name = 'countries'

urlpatterns = [
    path('', views.CountryListView.as_view(), name='list'),
    path('<str:pk>/', views.CountryDetailView.as_view(), name='detail'),
]
