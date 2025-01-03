from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, ItemCarrito, Carrito, Venta, ItemVenta
from .forms import ProductoForm, ItemCarritoForm
from django.contrib import messages
from django.db import models
from django.db.models import Count, Sum
from decimal import Decimal 
from django.templatetags.static import static
from PIL import Image
from django.conf import settings
import os

def get_carrito_total(request):
    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        carrito = Carrito.objects.filter(id=carrito_id).first()
        if carrito:
            return carrito.itemcarrito_set.aggregate(total=models.Sum('cantidad'))['total'] or 0
    return 0


def lista_productos(request):
    productos = Producto.objects.all()
    carrito_total = 0

    # Verifica si hay un carrito activo en la sesión
    if request.session.get('carrito_id'):
        try:
            carrito = Carrito.objects.get(id=request.session['carrito_id'])
            carrito_total = sum(item.cantidad for item in carrito.itemcarrito_set.all())
        except Carrito.DoesNotExist:
            pass

    return render(request, 'lista_productos.html', {'productos': productos, 'carrito_total': carrito_total})


# Añadir producto al sistema
def añadir_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # Asegúrate de que esta URL esté definida
        else:
            return render(request, 'añadir_producto.html', {'form': form, 'error': 'Formulario inválido'})
    else:
        form = ProductoForm()
    return render(request, 'añadir_producto.html', {'form': form})


def quitar_producto(request, producto_id):
    """
    Elimina un producto de la base de datos.
    """
    if request.method == 'POST':  # Asegúrate de que el método sea POST
        producto = get_object_or_404(Producto, id=producto_id)  # Busca el producto por ID
        producto.delete()  # Elimina el producto de la base de datos
        messages.success(request, f"El producto '{producto.nombre}' fue eliminado correctamente.")
    return redirect('lista_productos')  # Redirige a la lista de productos después



def estadisticas(request):
    from django.db.models import Count, Sum

    # Total de ingresos de todas las ventas
    total_ingresos = Venta.objects.aggregate(Sum('total'))['total__sum'] or 0

    # Cantidad total de ventas realizadas
    total_ventas = Venta.objects.count()

    # Cantidad total de productos vendidos
    productos_vendidos = ItemVenta.objects.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0

    # Promedio de ingresos por venta
    promedio_ingreso = total_ingresos / total_ventas if total_ventas > 0 else 0

    # Obtén los productos más vendidos (top 5)
    productos_populares_qs = (
        ItemVenta.objects.values('producto__nombre')
        .annotate(total_vendidos=Sum('cantidad'))
        .order_by('-total_vendidos')[:5]
    )

    productos_populares_labels = [item['producto__nombre'] for item in productos_populares_qs]
    productos_populares_data = [item['total_vendidos'] for item in productos_populares_qs]

    # Ventas por método de pago
    ventas_por_metodo_qs = (
        Venta.objects.values('metodo_pago')
        .annotate(total_ventas=Count('id'), total_ingresos=Sum('total'))
    )

    ventas_por_metodo = {
        'labels': [v['metodo_pago'] for v in ventas_por_metodo_qs],
        'ventas': [v['total_ventas'] for v in ventas_por_metodo_qs],
        'ingresos': [v['total_ingresos'] for v in ventas_por_metodo_qs],
    }

    context = {
        'total_ingresos': total_ingresos,
        'total_ventas': total_ventas,
        'productos_vendidos': productos_vendidos,
        'promedio_ingreso': promedio_ingreso,
        'productos_populares': {
            'labels': productos_populares_labels,
            'data': productos_populares_data,
        },
        'ventas_por_metodo': ventas_por_metodo,  # Añadir al contexto
    }

    return render(request, 'estadisticas.html', context)




def ver_carrito(request):
    carrito, created = Carrito.objects.get_or_create(id=request.session.get('carrito_id'))
    items = carrito.itemcarrito_set.all()
    total = sum(item.subtotal for item in items)
    carrito_total = get_carrito_total(request)
    return render(request, 'ver_carrito.html', {'carrito': carrito, 'items': items, 'total': total, 'carrito_total': carrito_total})

def eliminar_item_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')


# Añadir producto al carrito

def añadir_al_carrito(request, producto_id):
    """
    Añade un producto al carrito con la cantidad especificada.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    carrito_id = request.session.get('carrito_id')

    # Crea un nuevo carrito si no existe
    if not carrito_id:
        carrito = Carrito.objects.create()
        request.session['carrito_id'] = carrito.id
    else:
        carrito = get_object_or_404(Carrito, id=carrito_id)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))  # Cantidad seleccionada
        item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)

        if creado:
            item.cantidad = cantidad  # Establece la cantidad inicial
        else:
            item.cantidad += cantidad  # Incrementa la cantidad si ya existe

        item.save()
        messages.success(request, f"Se añadieron {cantidad} unidad(es) de '{producto.nombre}' al carrito.")
        return redirect('ver_carrito')

    return render(request, 'añadir_al_carrito.html', {'producto': producto})


    

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
    """
    Confirma la compra y opcionalmente imprime la boleta con una imagen.
    """
    imprimir_boleta = request.POST.get('imprimir_boleta', '0')  # Captura si se desea imprimir la boleta
    metodo_pago = request.POST.get('metodo_pago', 'efectivo')  # Captura el método de pago
    carrito_id = request.session.get('carrito_id')

    if not carrito_id:
        messages.error(request, "El carrito está vacío.")
        return redirect('ver_carrito')

    carrito = get_object_or_404(Carrito, id=carrito_id)
    items = carrito.itemcarrito_set.all()

    if not items:
        messages.error(request, "No hay productos en el carrito.")
        return redirect('ver_carrito')

    # Registrar la venta
    total = sum(item.subtotal for item in items)
    venta = Venta.objects.create(total=total, metodo_pago=metodo_pago)
    for item in items:
        ItemVenta.objects.create(
            venta=venta,
            producto=item.producto,
            cantidad=item.cantidad,
            precio=item.producto.precio,
        )

    # Vaciar el carrito
    carrito.delete()
    del request.session['carrito_id']

    # Generar boleta si se requiere
  # Generar boleta si se requiere
    if imprimir_boleta == '1':
        try:
            # Encabezado del ticket con adornos
            ticket_content = (
                f"\n"
                f"{'=' * 32}\n"
                f"{'PHILIA':^32}\n"
                f"{'=' * 32}\n"
                f"\n"
                f"Fecha: {venta.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'-' * 32}\n"
                f"Metodo de Pago: {venta.get_metodo_pago_display()}\n"
                f"{'-' * 32}\n"
                f"{'Producto':<16}{'Ctd':>4}{'Precio':>10}\n"
                f"{'-' * 32}\n"
            )

            # Detalles de los productos
            for item in venta.items.all():
                producto_nombre = item.producto.nombre[:14]  # Limita a 14 caracteres
                ticket_content += (
                    f"{producto_nombre:<14}{item.cantidad:>4}{item.precio:>10,.0f} CLP\n"
                )

            # Total
            ticket_content += (
                f"{'-' * 32}\n"
                f"{'Total:':<22}${venta.total:,.0f} CLP\n"
                f"{'-' * 32}\n"
                f"{' Gracias por su compra!':^32}\n"
                f"{'-' * 32}\n"
                f"{'@philiarave':^32}\n"
                f"{'' * 32}\n"
                f"\n"
            )

            # Configuración de la impresora
            printer_name = "philia1"  # Reemplaza con el nombre de tu impresora
            hprinter = win32print.OpenPrinter(printer_name)
            job = win32print.StartDocPrinter(hprinter, 1, ("Boleta", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, ticket_content.encode('ascii', 'replace'))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            win32print.ClosePrinter(hprinter)

            messages.success(request, f"Boleta para la venta #{venta.id} generada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al imprimir la boleta: {e}")


            # Configuración de la impresora
            printer_name = "philia1"  # Reemplaza con el nombre de tu impresora
            hprinter = win32print.OpenPrinter(printer_name)
            job = win32print.StartDocPrinter(hprinter, 1, ("Boleta", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, ticket_content.encode('ascii', 'replace'))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            win32print.ClosePrinter(hprinter)

            messages.success(request, f"Boleta para la venta #{venta.id} generada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al imprimir la boleta: {e}")
    else:
        messages.success(request, f"Venta #{venta.id} confirmada sin boleta. Método de pago: {venta.get_metodo_pago_display()}.")


    return redirect('lista_ventas')



# Lista de ventas realizadas
def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'listar_ventas.html', {'ventas': ventas})



# Eliminar un producto del carrito
def eliminar_del_carrito(request, item_id):
    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        carrito = get_object_or_404(Carrito, id=carrito_id)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        item.delete()
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')



import win32print
import win32api

def registrar_venta(request):
    """
    Registra una venta a partir del carrito del usuario.
    """
    carrito_id = request.session.get('carrito_id')
    if not carrito_id:
        messages.error(request, "El carrito está vacío.")
        return None

    carrito = get_object_or_404(Carrito, id=carrito_id)
    items = carrito.itemcarrito_set.all()

    if not items:
        messages.error(request, "No hay productos en el carrito.")
        return None

    total = sum(item.subtotal for item in items)
    venta = Venta.objects.create(total=total)

    for item in items:
        ItemVenta.objects.create(
            venta=venta,
            producto=item.producto,
            cantidad=item.cantidad,
            precio=item.producto.precio,
        )

    carrito.delete()
    del request.session['carrito_id']
    return venta




def confirmar_sin_boleta(request):
    """
    Confirma la venta sin generar boleta e imprime el contenido en la consola.
    """
    venta = registrar_venta(request)
    if not venta:
        return redirect('ver_carrito')  # Si no hay productos, redirigir al carrito

    # Calcula el IVA y el total con IVA
    iva = venta.total * Decimal('0.19')
    total_con_iva = venta.total + iva

    # Genera el contenido del ticket
    ticket_content = f"""
    ********************************
           PHILIA STORE            
    ********************************
    Fecha: {venta.fecha.strftime('%Y-%m-%d %H:%M:%S')}
    -------------------------------
    Producto         Cantidad   Total
    -------------------------------
    """
    for item in venta.items.all():
        ticket_content += f"{item.producto.nombre[:15]:<15} {item.cantidad:>3} x ${item.precio:>6,.0f} = ${item.subtotal:,.0f}\n"
    ticket_content += f"""
    -------------------------------
    Subtotal:         ${venta.total:,.0f}
    IVA (19%):        ${iva:,.0f}
    -------------------------------
    TOTAL:            ${total_con_iva:,.0f}
    -------------------------------
    ¡Gracias por su compra!
    ********************************
    """

    # Muestra el ticket en la consola
    print(ticket_content)

    # Mensaje de confirmación al usuario
    messages.success(request, f"Venta #{venta.id} confirmada sin boleta.")
    return redirect('lista_ventas')


def historial_ventas(request):
    ventas = Venta.objects.all()
    monto_total = sum(venta.total for venta in ventas)  # Total de todas las ventas
    return render(request, 'historial_ventas.html', {'ventas': ventas, 'monto_total': monto_total})



def imprimir_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    # Lógica para generar la boleta (por ejemplo, un PDF o redirigir a una vista detallada)
    messages.success(request, f"Boleta para la venta #{venta_id} generada.")
    return redirect('lista_ventas')  # Redirige al historial

def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    messages.success(request, f"La venta #{venta_id} ha sido eliminada.")
    return redirect('lista_ventas')  # Redirige al historial





def imprimir_ticket(request, venta_id):
    """
    Imprime un ticket con el formato atractivo y moderno, usando '.' como separador de miles.
    """
    # Obtén la venta usando el ID
    venta = get_object_or_404(Venta, id=venta_id)
    items = venta.items.all()

    try:
        # Encabezado del ticket con adornos
        ticket_content = (
            f"\n"
            f"{'=' * 32}\n"
            f"{'PHILIA':^32}\n"
            f"{'=' * 32}\n"
            f"\n"
            f"Fecha: {venta.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'-' * 32}\n"
            f"Metodo de Pago: {venta.get_metodo_pago_display()}\n"
            f"{'-' * 32}\n"
            f"{'Producto':<16}{'Ctd':>4}{'Precio':>10}\n"
            f"{'-' * 32}\n"
        )

        # Detalles de los productos
        for item in items:
            producto_nombre = item.producto.nombre[:14]  # Limita a 14 caracteres
            ticket_content += (
                f"{producto_nombre:<14}{item.cantidad:>4}"
                f"{item.precio:>10,.0f} CLP\n".replace(',', '.')
            )

        # Total
        total_formatted = f"{venta.total:,.0f}".replace(',', '.')
        ticket_content += (
            f"{'-' * 32}\n"
            f"{'Total:':<22}${total_formatted} CLP\n"
            f"{'-' * 32}\n"
            f"{' Gracias por su compra!':^32}\n"
            f"{'-' * 32}\n"
            f"{'@philiarave':^32}\n"
            f"{'' * 32}\n"
            f"\n"
        )

        # Configuración de la impresora
        printer_name = "philia1"  # Reemplaza con el nombre exacto de tu impresora
        hprinter = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(hprinter, 1, ("Boleta", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, ticket_content.encode('ascii', 'replace'))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)

        messages.success(request, f"El ticket para la venta #{venta.id} se imprimió correctamente.")
    except Exception as e:
        messages.error(request, f"Error al imprimir el ticket: {e}")

    # Redirigir a la lista de ventas después de la impresión
    return redirect('lista_ventas')


