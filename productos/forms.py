# productos/forms.py
from django import forms
from .models import Producto, ItemCarrito

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad']

class ItemCarritoForm(forms.ModelForm):
    class Meta:
        model = ItemCarrito
        fields = ['cantidad']

    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None)
        super().__init__(*args, **kwargs)
        if self.producto:
            self.fields['cantidad'].widget.attrs.update({'min': 1, 'max': self.producto.cantidad})

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if self.producto and cantidad > self.producto.cantidad:
            raise forms.ValidationError(f'La cantidad máxima disponible es {self.producto.cantidad}.')
        return cantidad


from django import forms
from .models import ItemCarrito

class ItemCarritoForm(forms.ModelForm):
    class Meta:
        model = ItemCarrito
        fields = ['cantidad']

    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None)
        super().__init__(*args, **kwargs)
        if self.producto:
            self.fields['cantidad'].widget.attrs.update({'min': 1, 'max': self.producto.cantidad})

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if self.producto and cantidad > self.producto.cantidad:
            raise forms.ValidationError(f'La cantidad máxima disponible es {self.producto.cantidad}.')
        return cantidad
