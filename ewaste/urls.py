from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('facilities/', views.facilities, name='facilities'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report-ewaste/', views.report_ewaste, name='report_ewaste'),
    path('my-items/', views.my_items, name='my_items'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('manage-pickups/', views.manage_pickups, name='manage_pickups'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('company-admin/', views.company_admin, name='company_admin'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    path('pickup/<int:pickup_id>/edit/', views.edit_pickup, name='edit_pickup'),
    path('users/', views.user_list, name='user_list'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('search/', views.search_items, name='search'),
]
