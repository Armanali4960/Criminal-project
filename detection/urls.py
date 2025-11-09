from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='citizen_dashboard'),
    path('police/', views.police_dashboard, name='police_dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('report/<uuid:report_id>/', views.get_report_details, name='report_details'),
    path('verify/<uuid:detection_id>/', views.verify_detection, name='verify_detection'),
    path('confirm-criminal/<uuid:detection_id>/', views.confirm_criminal_status, name='confirm_criminal'),
    path('bulk-upload-criminals/', views.bulk_upload_criminals, name='bulk_upload_criminals'),
    path('login/', views.citizen_login, name='citizen_login'),
    path('police/login/', views.police_login, name='police_login'),
    path('logout/', views.citizen_logout, name='citizen_logout'),
    path('police/logout/', views.police_logout, name='police_logout'),
    path('register/', views.register_citizen, name='register_citizen'),
    path('camera/', views.camera_page, name='camera_page'),
    path('test/', views.test_view, name='test_view'),  # Test view for debugging
]