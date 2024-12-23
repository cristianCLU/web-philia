from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def calcular_total(self):
        return sum(item.subtotal for item in self.items.all())

class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio

class Carrito(models.Model):
    productos = models.ManyToManyField(Producto, through='ItemCarrito')

    def calcular_total(self):
        return sum(item.subtotal for item in self.itemcarrito_set.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    añadido = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad
