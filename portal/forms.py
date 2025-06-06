# portal/forms.py

from django import forms
from .models import Product
from .models import Order, Product, CartItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock','image']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address', 'city', 'zip_code', 'delivery_method']
        widgets = {
            'delivery_method': forms.Select(choices=[('Inside Dhaka', 'Inside Dhaka'), ('Outside Dhaka', 'Outside Dhaka')]),
        }

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')
        if delivery_method == 'Inside Dhaka':
            cleaned_data['delivery_price'] = 60
        else:
            cleaned_data['delivery_price'] = 120
        return cleaned_data

