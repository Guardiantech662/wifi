from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

#from django.contrib.auth import views as auth_views
urlpatterns = [
    # Router Management (Admin only)
   # path('routers/', views.router_list, name='router_list'),
   # path('routers/create/', views.router_create, name='router_create'),

    # User Dashboard
    path('dashboard', views.dashboard, name='dashboard'),
    path('create_ticket', views.create_ticket, name='create_ticket'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # Payment Webhooks
    path('', views.signup, name='signup'),

    path('payment-notify/', views.payment_notify, name='payment_notify'),
    path('payment-return/', views.payment_return, name='payment_return'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
   # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
   # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
  


    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),


  
]
