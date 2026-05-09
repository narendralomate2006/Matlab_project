from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_list_view, name='test_list'),
    path('test/<int:test_id>/', views.test_window_view, name='test_window'),
    path('test/<int:test_id>/submit/', views.submit_test_view, name='submit_test'),
    path('result/<int:attempt_id>/', views.test_result_view, name='test_result'),
    path('teacher-dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
]
