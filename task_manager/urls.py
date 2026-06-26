from django.urls import path

from task_manager import views

urlpatterns = [
    # generic
    path('stats/', views.TaskManagerDashboardAPIView.as_view(), name='task-manager-stats'),
    path("choices/", views.TaskChoicesView.as_view(), name="task-choices"),
    path("search/", views.TaskSearchView.as_view(), name="task-search"),
    path("list/", views.TaskListView.as_view(), name="task-list"),

    # personal
    path("personal/", views.PersonalTaskRUDView.as_view(), name="personal-task-rud"),
    path("personal/add/", views.PersonalTaskCreateView.as_view(), name="personal-task-create"),

    # organize
    path("organize/pending-approval/", views.PendingApprovalListView.as_view(), name="pending-approval-list"),
    path("organize/pending-approval/<int:pk>/approve/", views.ApproveTaskView.as_view(), name="task-approve"),
    path("organize/pending-approval/<int:pk>/reject/", views.RejectTaskView.as_view(), name="task-reject"),

    # ── organize — CRUD ───────────────────────────────────────────────────
    path("organize/<int:pk>/", views.OrganizeTaskRUDView.as_view(), name="organize-task-rud"),
    path("organize/add/", views.OrganizeTaskCreateView.as_view(), name="organize-task-create"),

]
