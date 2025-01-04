# productos/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('añadir/', views.añadir_producto, name='añadir_producto'),
    path('añadir_al_carrito/<int:producto_id>/', views.añadir_al_carrito, name='añadir_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('modificar_item_carrito/<int:item_id>/', views.modificar_item_carrito, name='modificar_item_carrito'),
    path('confirmar_compra/', views.confirmar_compra, name='confirmar_compra'),
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('confirmar_sin_boleta/', views.confirmar_sin_boleta, name='confirmar_sin_boleta'),
    path('imprimir_ticket/<int:venta_id>/', views.imprimir_ticket, name='imprimir_ticket'),
    path('eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('quitar/<int:producto_id>/', views.quitar_producto, name='quitar'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
]


