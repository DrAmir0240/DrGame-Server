from django.urls import path

from psn import views

urlpatterns = [
    # -------------------- Sony Accounts --------------------
    path(
        "personal/sony-users/",
        views.EmployeePanelOwnedSonyAccountList.as_view(),
        name="owned-sony-account-list",
    ),
    path(
        "personal/sony-users/<int:pk>/",
        views.EmployeePanelSonyAccountDetail.as_view(),
        name="sony-account-detail",
    ),
    path(
        "personal/sony-users/choices/",
        views.EmployeePanelSonyAccountChoices.as_view(),
        name="sony-users-choices",
    ),
    # ==================== SonyAccounts Views ====================
    path(
        "sony-users/new/",
        views.EmployeePanelGetNewSonyAccount.as_view(),
        name="sony-account-new",
    ),
    path(
        "sony-users/",
        views.EmployeePanelSonyAccountList.as_view(),
        name="sony-account-list",
    ),
    path(
        "sony-users/<int:pk>/",
        views.EmployeePanelSonyAccountDetail.as_view(),
        name="sony-account-detail",
    ),
    # ==================== PSN Website (Phase 2) ====================
    path("accounts/", views.PSNSonyAccountListCreateView.as_view()),
    path("accounts/<int:pk>/", views.PSNSonyAccountDetailView.as_view()),
    path(
        "accounts/<int:account_pk>/games/",
        views.PSNSonyAccountGameListCreateView.as_view(),
    ),
    path(
        "accounts/<int:account_pk>/games/<int:pk>/",
        views.PSNSonyAccountGameDetailView.as_view(),
    ),
    path("games/", views.PSNGameListView.as_view()),
    path("account-statuses/", views.PSNSonyAccountStatusListCreateView.as_view()),
    path("account-statuses/<int:pk>/", views.PSNSonyAccountStatusDetailView.as_view()),
    path("account-categories/", views.PSNSonyAccountCategoryListView.as_view()),
]
