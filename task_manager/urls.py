from django.urls import path

from task_manager import views

urlpatterns = [

# -------------------- Tasks --------------------
    path('personal/tasks/', views.EmployeePanelTaskList.as_view(), name='personal-task-list'),
    path('personal/tasks/<int:pk>/', views.EmployeePanelTaskDetail.as_view(), name='personal-task-detail'),
    path('personal/tasks/add/', views.EmployeePanelAddTask.as_view(), name='personal-task-add'),

    # ==================== TaskManager Views ====================
    path('tasks/', views.EmployeePanelOrganizeTaskListCreateView.as_view(), name='task-list-add'),
    path('tasks/<int:pk>/', views.EmployeePanelOrganizeTaskDetailView.as_view(), name='task-detail'),
    path('tasks/hr/', views.EmployeePanelOrganizeTaskChoices.as_view(), name='task-employee-list'),

]