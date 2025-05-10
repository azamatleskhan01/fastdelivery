from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

class ProductForm(forms.Form):
    name = forms.CharField(label='Product Name', max_length=100)
    price = forms.FloatField(label='Price', min_value=0.01)
    description = forms.CharField(label='Description', widget=forms.Textarea)

class CartItemForm(forms.Form):
    menu_item_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(label='Quantity', initial=1, validators=[MinValueValidator(1), MaxValueValidator(10)], widget=forms.NumberInput(attrs={'min': 1, 'max': 10}))

class UpdateCartItemForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity', validators=[MinValueValidator(1), MaxValueValidator(10)], widget=forms.NumberInput(attrs={'min': 1, 'max': 10}))

class OrderForm(forms.Form):
    delivery_latitude = forms.FloatField(widget=forms.HiddenInput)
    delivery_longitude = forms.FloatField(widget=forms.HiddenInput)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')