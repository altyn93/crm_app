from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('blocked/', views.blocked_view, name='blocked'),
    
    # Восстановление пароля
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset-confirm/<int:uid>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Клиенты
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_add, name='client_add'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Заявки
    path('orders/', views.order_list, name='order_list'),
    path('clients/<int:client_pk>/orders/add/', views.order_add, name='order_add'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # Экспорт
    path('export/clients/', views.export_clients, name='export_clients'),
    path('export/orders/', views.export_orders, name='export_orders'),
    
    # Аналитика
    path('analytics/', views.analytics, name='analytics'),
    
    # Сотрудники
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Приглашения сотрудников
    path('employees/invite/', views.employee_invite, name='employee_invite'),
    path('employees/invitations/', views.employee_invitations, name='employee_invitations'),
    path('register/invite/<str:token>/', views.register_by_invitation, name='register_by_invitation'),
    
    # Чат
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:employee_pk>/', views.chat_detail, name='chat_detail'),
    
    # Время работы
    path('work/start/', views.start_work, name='start_work'),
    path('work/end/', views.end_work, name='end_work'),
    path('work/report/', views.work_time_report, name='work_time_report'),
    path('work/employee/<int:employee_pk>/', views.employee_work_time, name='employee_work_time'),
    
    # Язык
    path('language/<str:lang>/', views.change_language, name='change_language'),
]

