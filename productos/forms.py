# productos/forms.py
from django import forms
from .models import Producto, ItemCarrito


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',  # Tamaño grande
                'placeholder': 'Ingrese el nombre del producto',
                'style': (
                    'border: 2px solid #888; '
                    'background-color: #1e1e1e; '
                    'color: #f8f9fa; '
                    'border-radius: 10px; '
                    'padding: 15px; '
                    'font-size: 1.3rem; '  # Letras más grandes
                    'font-weight: bold;'  # Letras más gorditas
                ),
                'maxlength': '100',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ingrese una descripción detallada del producto (opcional)',
                'rows': 4,  # Ajusta la altura del campo
                'style': (
                    'border: 2px solid #888; '
                    'background-color: #1e1e1e; '
                    'color: #f8f9fa; '
                    'border-radius: 10px; '
                    'padding: 15px; '
                    'font-size: 1.3rem; '  # Letras más grandes
                    'font-weight: bold;'  # Letras más gorditas
                ),
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '$ Ingrese el precio',
                'style': (
                    'border: 2px solid #888; '
                    'background-color: #1e1e1e; '
                    'color: #f8f9fa; '
                    'border-radius: 10px; '
                    'padding: 15px; '
                    'font-size: 1.3rem; '  # Letras más grandes
                    'font-weight: bold;'  # Letras más gorditas
                ),
                'min': '0',  # Precio mínimo
                'step': '0.01',  # Permitir decimales
            }),
        }


        
        

class ItemCarritoForm(forms.ModelForm):
    class Meta:
        model = ItemCarrito
        fields = ['cantidad']

    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None)
        super().__init__(*args, **kwargs)
        # Solo configurar el atributo 'min' sin referencia a un 'max'
        self.fields['cantidad'].widget.attrs.update({'min': 1})

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad < 1:
            raise forms.ValidationError('La cantidad debe ser al menos 1.')
        return cantidad
