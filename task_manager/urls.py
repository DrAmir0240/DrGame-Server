from django.urls import path

from task_manager import views

urlpatterns = [
    # generic
    path('stats/', views.TaskManagerDashboardAPIView.as_view(), name='task-manager-stats'),
    # path('choices/'),
    # path('search/'),

    # list
    # path('list/<str:status>/'),
    # path('list/<int:employee_id>/'),
    # path('list/<str:priority>/'),
    # path('list/<str:type>/')

    # personal
    # path('read-delete-update/personal'),
    # path('add/personal'),

    # organize
    # path('list/pending-approval/'),
    # path('list/pending-approval/approve/'),
    # path('list/pending-approval/reject/'),
    # path('read-delete-update/<int:pk>'),
    # path('add/'),

]
