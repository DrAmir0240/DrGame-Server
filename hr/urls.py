from django.urls import path
from hr import views

urlpatterns = [
    # Permissions
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    path('my-permissions/', views.MyPermissionsView.as_view(), name='my-permissions'),

    # Roles
    path('roles/', views.EmployeeRoleListView.as_view(), name='role-list'),
    path('roles/create/', views.EmployeeRoleCreateView.as_view(), name='role-create'),
    path('roles/<int:pk>/', views.EmployeeRoleDetailView.as_view(), name='role-detail'),
    path('roles/<int:pk>/update/', views.EmployeeRoleUpdateView.as_view(), name='role-update'),
    path('roles/<int:pk>/delete/', views.EmployeeRoleDeleteView.as_view(), name='role-delete'),
]
