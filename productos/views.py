from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, ItemCarrito, Carrito, Venta, ItemVenta
from .forms import ProductoForm, ItemCarritoForm
from django.contrib import messages
from django.db import models
from django.db.models import Sum

def get_carrito_total(request):
    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        carrito = Carrito.objects.filter(id=carrito_id).first()
        if carrito:
            return carrito.itemcarrito_set.aggregate(total=models.Sum('cantidad'))['total'] or 0
    return 0

def lista_productos(request):
    productos = Producto.objects.all()
    carrito_total = get_carrito_total(request)
    return render(request, 'lista_productos.html', {'productos': productos, 'carrito_total': carrito_total})

def añadir_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'añadir_producto.html', {'form': form})

def añadir_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito_id = request.session.get('carrito_id')
    if not carrito_id:
        carrito = Carrito.objects.create()
        request.session['carrito_id'] = carrito.id
    else:
        carrito = Carrito.objects.get(id=carrito_id)

    if request.method == 'POST':
        form = ItemCarritoForm(request.POST, producto=producto)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            if cantidad <= producto.cantidad:
                item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
                if not created:
                    if item.cantidad + cantidad <= producto.cantidad:
                        item.cantidad += cantidad
                    else:
                        messages.error(request, 'Cantidad insuficiente en inventario.')
                        return redirect('añadir_al_carrito', producto_id=producto_id)
                else:
                    item.cantidad = cantidad
                item.save()

                # Actualizar el stock del producto
                producto.cantidad -= cantidad
                producto.save()

                messages.success(request, 'Producto añadido al carrito.')
                return redirect('ver_carrito')
            else:
                messages.error(request, 'Cantidad insuficiente en inventario.')
                return redirect('añadir_al_carrito', producto_id=producto_id)
    else:
        form = ItemCarritoForm(initial={'cantidad': 1}, producto=producto)

    return render(request, 'añadir_al_carrito.html', {'form': form, 'producto': producto})
    
def ver_carrito(request):
    carrito, created = Carrito.objects.get_or_create(id=request.session.get('carrito_id'))
    items = carrito.itemcarrito_set.all()
    total = sum(item.subtotal for item in items)
    carrito_total = get_carrito_total(request)
    return render(request, 'ver_carrito.html', {'carrito': carrito, 'items': items, 'total': total, 'carrito_total': carrito_total})

def eliminar_item_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    item.delete()
    return redirect('ver_carrito')

def modificar_item_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if request.method == 'POST':
        form = ItemCarritoForm(request.POST, instance=item)
        if form.is_valid():
            nueva_cantidad = form.cleaned_data['cantidad']
            if nueva_cantidad <= item.producto.cantidad + item.cantidad:
                diferencia = nueva_cantidad - item.cantidad
                item.cantidad = nueva_cantidad
                item.save()
                messages.success(request, 'Cantidad actualizada.')
                return redirect('ver_carrito')
            else:
                messages.error(request, 'Cantidad insuficiente en inventario.')
    else:
        form = ItemCarritoForm(instance=item)
    return render(request, 'modificar_item_carrito.html', {'form': form})

def confirmar_compra(request):
    carrito_id = request.session.get('carrito_id')
    carrito = get_object_or_404(Carrito, id=carrito_id)
    items = carrito.itemcarrito_set.all()
    total = sum(item.subtotal for item in items)
    venta = Venta.objects.create(total=total)

    for item in items:
        producto = item.producto
        if item.cantidad <= producto.cantidad:
            producto.cantidad -= item.cantidad
            producto.save()
            ItemVenta.objects.create(venta=venta, producto=item.producto, cantidad=item.cantidad, precio=item.producto.precio)
        else:
            messages.error(request, f'Cantidad insuficiente en inventario para {producto.nombre}.')
            return redirect('ver_carrito')

    carrito.delete()
    del request.session['carrito_id']
    messages.success(request, 'Compra realizada con éxito.')
    return redirect('lista_ventas')

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'listar_ventas.html', {'ventas': ventas})

def eliminar_del_carrito(request, item_id):
    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        carrito = get_object_or_404(Carrito, id=carrito_id)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        
        # Restaurar la cantidad en el inventario
        producto = item.producto
        producto.cantidad += item.cantidad
        producto.save()

        # Eliminar el item del carrito
        item.delete()

        messages.success(request, 'Producto eliminado del carrito y cantidad restaurada al inventario.')
    
    return redirect('ver_carrito')