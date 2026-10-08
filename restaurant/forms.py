from django import forms
from .models import Order


TABLE_CHOICES = [
    ('', '-- Select Your Table / Order Type --'),
    ('Table 1', 'Table 1 (Indoor Window)'),
    ('Table 2', 'Table 2 (Indoor Center)'),
    ('Table 3', 'Table 3 (Indoor Booth)'),
    ('Table 4', 'Table 4 (Patio Garden)'),
    ('Table 5', 'Table 5 (Patio Garden)'),
    ('Table 6', 'Table 6 (Private Dining)'),
    ('Bar 1', 'Bar Counter Seat 1'),
    ('Bar 2', 'Bar Counter Seat 2'),
    ('Takeout', 'Takeout / Pickup Counter'),
]


class OrderCheckoutForm(forms.ModelForm):
    table_number = forms.ChoiceField(
        choices=TABLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': 'required',
            'id': 'table_number'
        })
    )

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_phone',
            'customer_email',
            'table_number',
            'special_instructions',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Alex Johnson',
                'required': 'required',
                'autocomplete': 'name',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +1 (555) 019-2834',
                'required': 'required',
                'autocomplete': 'tel',
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. alex@example.com (optional)',
                'autocomplete': 'email',
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any allergies, spice level, or special preparation requests? (optional)',
                'rows': 3,
            }),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
