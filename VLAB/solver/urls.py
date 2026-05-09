from django.urls import path
from . import views

urlpatterns = [
    path('solve/', views.solver_view, name='solver'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('analytics/', views.student_analytics_view, name='student_analytics'),
    path('admin-analytics/', views.admin_dashboard, name='admin_analytics'),
]
