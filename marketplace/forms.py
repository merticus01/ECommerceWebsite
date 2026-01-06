from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from .models import User, Product


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Your password'}))


class BuyerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_buyer = True
        user.is_seller = False
        user.save()
        return user


class SellerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_seller = True
        user.is_buyer = False
        user.save()
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'slug',
            'era',
            'category',
            'condition',
            'description',
            'story',
            'measurements',
            'materials',
            'sustainability_tags',
            'price',
            'inventory',
            'product_image',
            'is_active',
            'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL-friendly name (auto-generated)'}),
            'era': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'story': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share the provenance or story'}),
            'measurements': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10" x 8" x 5"'}),
            'materials': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., silk, wood, brass'}),
            'sustainability_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., deadstock, upcycled, locally sourced'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in USD', 'step': '0.01'}),
            'inventory': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity available'}),
            'product_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


