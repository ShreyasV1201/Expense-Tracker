"""
URL configuration for expenseTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from expenseTracker.views import (
    MyLoginView, MyLogoutView, register, home, add_expense, edit_expense, delete_expense,
    income_tracker, edit_income, delete_income, add_income, 
    profile, recurring_expenses, edit_recurring_expense,delete_recurring_expense, export_expenses, export_incomes, dashboard,
    expense_pie_chart,income_expense_bar_chart
)

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('',      dashboard, name='home'),

    path('add-expense/', add_expense, name='add_expense'),
    path('expense/<int:pk>/edit/', edit_expense, name='edit_expense'),
    path('expenses/<int:pk>/delete/', delete_expense, name='delete_expense'),

    path('income/', income_tracker, name='income_tracker'),
    path('income/add/', add_income, name='add_income'),
    path('income/<int:pk>/edit/', edit_income, name='edit_income'),
    path('income/<int:pk>/delete/', delete_income, name='delete_income'),

    path('profile/', profile, name='profile'),

    path('recurring-expenses/',  recurring_expenses, name='recurring_expenses'),
    path('edit/<int:pk>/', edit_recurring_expense, name='edit_recurring_expense'),
    path('recurring-expenses/delete/<int:pk>/',delete_recurring_expense, name='delete_recurring_expense'),

     path('export-expenses/', export_expenses, name='export_expenses'),
      path('incomes/export/', export_incomes, name='export_incomes'  ),
      path("dashboard/", dashboard, name="dashboard"),

     path('admin/', admin.site.urls),   

    path('expense-chart/', expense_pie_chart, name='expense_chart'),
    path('inc-exp-chart/',    income_expense_bar_chart, name='inc_exp_chart'),
]
