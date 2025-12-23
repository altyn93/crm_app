from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BusinessProfile, Client, Order, Comment, Employee, Message


class RegisterForm(UserCreationForm):
    """Форма регистрации"""
    business_name = forms.CharField(max_length=200, label='Название бизнеса')
    phone = forms.CharField(max_length=50, label='Телефон для связи')
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'business_name', 'phone']


class ClientForm(forms.ModelForm):
    """Форма клиента"""
    class Meta:
        model = Client
        fields = ['name', 'phone', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    """Форма заявки"""
    class Meta:
        model = Order
        fields = ['service', 'status', 'price', 'completed_at']


class CommentForm(forms.ModelForm):
    """Форма комментария"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }


class EmployeeForm(forms.ModelForm):
    """Форма сотрудника"""
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email', 'role', 'is_active']


class MessageForm(forms.ModelForm):
    """Форма сообщения"""
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }
