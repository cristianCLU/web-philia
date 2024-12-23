from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def clp(value):
    """Convierte un número a formato de pesos chilenos con puntos como separadores"""
    try:
        value = float(value)
        # Usar formato con separadores de miles en español
        return f"${value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value
    
@register.filter
def sum_total(ventas):
    """
    Calcula el monto total de todas las ventas.
    """
    if not ventas:
        return Decimal(0)
    return sum(venta.total for venta in ventas)



@register.filter
def get_producto_nombre(producto):
    return producto.producto__nombre