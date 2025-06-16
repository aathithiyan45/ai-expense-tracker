from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('export/csv/', views.export_expenses_csv, name='export_csv'),
    path('export/pdf/', views.export_expenses_pdf, name='export_pdf'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
