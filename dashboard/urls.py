from django.urls import path

from dashboard import views

urlpatterns = [
    # ==================== Stats Views ====================
    path('stats/employee-tasks/', views.TaskStatsAPIView.as_view(), name="employee-task-stats"),
    path('stats/game-orders/', views.GameOrderStatsAPIView.as_view(), name="game-order-stats"),
    path('stats/game-orders/personal/', views.PersonalGameOrderStatsAPIView.as_view(),
         name="personal-game-order-stats"),
    path('stats/product-orders/', views.ProductOrderStatsAPIView.as_view(), name="product-order-stats"),
    path('stats/repair-orders/', views.RepairOrderStatsAPIView.as_view(), name="repair-order-stats"),
    path('stats/finance/', views.FinanceSummaryAPIView.as_view(), name="finance-stats"),
    path('stats/hr/', views.EmployeeStatsAPIView.as_view(), name="hr-stats"),
    path('stats/crm/', views.CustomerStatsAPIView.as_view(), name="crm-stats"),
    path('stats/real-assets/', views.RealAssetStatsAPIView.as_view(), name="real-assets-stats"),
    path('stats/products/', views.ProductsStatsAPIView.as_view(), name="products-stats"),

    # ==================== Reports Views ====================
    path('reports/sell/', views.SellReportsAPIView.as_view(), name="sell-reports"),
    path('reports/finance/', views.FinanceReportsAPIView.as_view(), name="finance-reports"),
    path('reports/employee/', views.PerFormanceReportAPIView.as_view(), name="employee-reports"),
    path('reports/customer/', views.CustomerReportAPIView.as_view(), name="customer-reports"),
]
