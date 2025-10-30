from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactRequestView.as_view(), name='contact_request'),
    path('request-kp/', views.RequestKPView.as_view(), name='request_kp'),
]
