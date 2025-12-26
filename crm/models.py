from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets


class BusinessProfile(models.Model):
    """Профиль бизнеса"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Русский'),
        ('tk', 'Türkmen'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField('Название бизнеса', max_length=200)
    language = models.CharField('Язык', max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    is_active = models.BooleanField('Активен', default=False)
    subscription_end = models.DateField('Подписка до', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    notes = models.TextField('Заметки админа', blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    # Максимальное число сотрудников для этого бизнеса (по умолчанию 20)
    max_employees = models.PositiveIntegerField('Максимум сотрудников', default=20)
    
    def __str__(self):
        return self.business_name
    
    def is_subscription_valid(self):
        from datetime import date
        if not self.is_active:
            return False
        if self.subscription_end and self.subscription_end < date.today():
            return False
        return True


class Client(models.Model):
    """Клиент"""
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField('Имя', max_length=200)
    phone = models.CharField('Телефон', max_length=50)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    class Meta:
        ordering = ['-created_at']


class Order(models.Model):
    """Заявка"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('done', 'Завершена'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    service = models.CharField('Услуга', max_length=200)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    def __str__(self):
        return f"{self.service} - {self.client.name}"
    
    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """Комментарий к заявке"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField('Текст')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий к {self.order}"
    
    class Meta:
        ordering = ['created_at']


class Employee(models.Model):
    """Сотрудник бизнеса"""
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('specialist', 'Специалист'),
        ('admin', 'Администратор'),
    ]
    
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    role = models.CharField('Должность', max_length=20, choices=ROLE_CHOICES, default='specialist')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['first_name', 'last_name']
        unique_together = ['business', 'user']


class Message(models.Model):
    """Сообщение в чате"""
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient}"
    
    class Meta:
        ordering = ['-created_at']

class WorkLog(models.Model):
    """Логирование времени работы сотрудника"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_logs')
    start_time = models.DateTimeField('Время начала работы')
    end_time = models.DateTimeField('Время конца работы', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def duration(self):
        """Вычисляет продолжительность работы"""
        if self.end_time:
            return self.end_time - self.start_time
        else:
            from django.utils import timezone
            return timezone.now() - self.start_time
    
    @property
    def is_active(self):
        """Проверяет, активна ли сессия работы"""
        return self.end_time is None
    
    class Meta:
        ordering = ['-start_time']


class EmployeeInvitation(models.Model):
    """Приглашение для регистрации сотрудника"""
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='employee_invitations')
    email = models.EmailField('Email')
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    role = models.CharField('Должность', max_length=20, choices=Employee.ROLE_CHOICES, default='specialist')
    
    # Уникальный токен для приглашения
    token = models.CharField('Токен приглашения', max_length=100, unique=True, default=secrets.token_urlsafe)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Дополнительная информация
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField('Дата приглашения', auto_now_add=True)
    accepted_at = models.DateTimeField('Дата принятия', null=True, blank=True)
    
    def __str__(self):
        return f"Приглашение для {self.email} ({self.business.business_name})"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['business', 'email']