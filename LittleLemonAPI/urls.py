from django.urls import path,include
from . import views

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('menu-items/', views.menuitems),
    path('menu-items/<int:pk>/', views.menuitem),
    path('groups/manager/users/', views.managers),
    path('groups/manager/users/<int:pk>/', views.remove_manager),
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('groups/delivery-crew/users/<int:pk>/', views.remove_delivery),
    path('cart/menu-items/', views.cart),
    path('orders/', views.orders),
    path('orders/<int:pk>/', views.SingleOrder),
]