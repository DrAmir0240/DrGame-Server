from django.urls import path

from task_manager import views

urlpatterns = [
    path('stats/', views.PlannedTaskManagerDashboardAPIView.as_view(), name='task-manager-stats'),
    path("choices/", views.TaskChoicesView.as_view(), name="task-choices"),

    # =======> Planned Tasks <=======#
    # generic
    path("search/", views.PlannedTaskSearchView.as_view(), name="task-search"),
    path("list/", views.PlannedTaskListView.as_view(), name="task-list"),

    # personal
    path("personal/<int:pk>/", views.PersonalPlannedTaskRUDView.as_view(), name="personal-task-rud"),
    path("personal/add/", views.PersonalPlannedTaskCreateView.as_view(), name="personal-task-create"),

    # organize
    path("organize/pending-approval/", views.PendingApprovalPlannedTaskListView.as_view(), name="pending-approval-list"),
    path("organize/pending-approval/<int:pk>/approve/", views.ApprovePlannedTaskView.as_view(), name="task-approve"),
    path("organize/pending-approval/<int:pk>/reject/", views.RejectPlannedTaskView.as_view(), name="task-reject"),
    path("organize/<int:pk>/", views.OrganizePlannedTaskRUDAPIView.as_view(), name="organize-task-rud"),
    path("organize/add/", views.OrganizePlannedTaskCreateView.as_view(), name="organize-task-create"),

    # =======> Daily Tasks <=======#
    # generic
    path("daily-tasks/list/", views.DailyTaskListAPIView, name='daily-task-list'),
    path("daily-tasks/search/", views.DailyTaskSearchAPIView, name='daily-task-search'),

    # personal
    path("daily-tasks/add/", views.PersonalDailyTaskCreateAPIView, name='personal-daily-task-add'),
    path("daily-tasks/<int:pk>/", views.PersonalDailyTaskRUDAPIView, name='personal-daily-task-rud'),

    # organize
    path("daily-tasks/organize/add/", views.OrganizeDailyTaskCreateAPIView, name='organize-daily-task-add'),
    path("daily-tasks/organize/<int:pk>", views.OrganizeDailyTaskRUDAPIView, name='organize-daily-task-rud'),
]
