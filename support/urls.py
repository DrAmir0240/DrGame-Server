from django.urls import path

from support import views

urlpatterns = [
    path(
        "",
        views.EmployeeTicketListView.as_view(),
        name="support-ticket-list",
    ),
    path(
        "<int:pk>/",
        views.EmployeeTicketDetailView.as_view(),
        name="support-ticket-detail",
    ),
    path(
        "<int:pk>/assign/",
        views.EmployeeTicketAssignView.as_view(),
        name="support-ticket-assign",
    ),
    path(
        "<int:pk>/status/",
        views.EmployeeTicketStatusView.as_view(),
        name="support-ticket-status",
    ),
    path(
        "<int:pk>/internal-note/",
        views.EmployeeTicketInternalNoteView.as_view(),
        name="support-ticket-internal-note",
    ),
]
