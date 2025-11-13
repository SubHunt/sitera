from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactRequestView.as_view(), name='contact_request'),
    path('page/', views.ContactPageView.as_view(), name='contact_page'),
    path('request-kp/', views.RequestKPView.as_view(), name='request_kp'),
    path('consultation/', views.ConsultationRequestView.as_view(), name='consultation'),
]
