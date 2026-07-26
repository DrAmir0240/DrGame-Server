from django.urls import path

from support import views

urlpatterns = [
    path(
        "",
        views.CustomerTicketListView.as_view(),
        name="customer-ticket-list",
    ),
    path(
        "<int:pk>/",
        views.CustomerTicketDetailView.as_view(),
        name="customer-ticket-detail",
    ),
    path(
        "create/",
        views.CustomerTicketCreateView.as_view(),
        name="customer-ticket-create",
    ),
    path(
        "<int:pk>/reply/",
        views.CustomerTicketReplyView.as_view(),
        name="customer-ticket-reply",
    ),
    path(
        "<int:pk>/messages/",
        views.CustomerTicketMessagesView.as_view(),
        name="customer-ticket-messages",
    ),
]
