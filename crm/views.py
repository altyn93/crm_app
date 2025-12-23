from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Sum, Count, Avg
from django.http import HttpResponse, JsonResponse
from django.utils import translation
from django.utils.timezone import now
from datetime import timedelta, datetime
from openpyxl import Workbook
import json
from .models import BusinessProfile, Client, Order, Comment, Employee, Message, WorkLog
from .forms import RegisterForm, ClientForm, OrderForm, CommentForm


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            BusinessProfile.objects.create(
                user=user,
                business_name=form.cleaned_data['business_name'],
                phone=form.cleaned_data.get('phone', ''),
                is_active=False  # По умолчанию неактивен до оплаты
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'crm/register.html', {'form': form})


@login_required
def blocked_view(request):
    """Страница для заблокированных пользователей"""
    return render(request, 'crm/blocked.html')


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'crm/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Главная страница"""
    profile = request.user.businessprofile
    clients_count = Client.objects.filter(business=profile).count()
    orders_new = Order.objects.filter(client__business=profile, status='new').count()
    orders_in_progress = Order.objects.filter(client__business=profile, status='in_progress').count()
    
    return render(request, 'crm/dashboard.html', {
        'profile': profile,
        'clients_count': clients_count,
        'orders_new': orders_new,
        'orders_in_progress': orders_in_progress,
    })


@login_required
def client_list(request):
    """Список клиентов"""
    profile = request.user.businessprofile
    clients = Client.objects.filter(business=profile)
    
    search = request.GET.get('search', '')
    if search:
        clients = clients.filter(Q(name__icontains=search) | Q(phone__icontains=search))
    
    return render(request, 'crm/client_list.html', {'clients': clients, 'search': search})


@login_required
def client_add(request):
    """Добавить клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.business = request.user.businessprofile
            client.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'crm/client_form.html', {'form': form, 'title': 'Добавить клиента'})


@login_required
def client_edit(request, pk):
    """Редактировать клиента"""
    client = get_object_or_404(Client, pk=pk, business=request.user.businessprofile)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'crm/client_form.html', {'form': form, 'title': 'Редактировать клиента'})


@login_required
def client_detail(request, pk):
    """Детали клиента и его заявки"""
    client = get_object_or_404(Client, pk=pk, business=request.user.businessprofile)
    orders = client.orders.all()
    return render(request, 'crm/client_detail.html', {'client': client, 'orders': orders})


@login_required
def client_delete(request, pk):
    """Удалить клиента"""
    client = get_object_or_404(Client, pk=pk, business=request.user.businessprofile)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'crm/confirm_delete.html', {'object': client, 'type': 'клиента'})


@login_required
def order_add(request, client_pk):
    """Добавить заявку"""
    client = get_object_or_404(Client, pk=client_pk, business=request.user.businessprofile)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()
            return redirect('client_detail', pk=client_pk)
    else:
        form = OrderForm()
    return render(request, 'crm/order_form.html', {'form': form, 'client': client, 'title': 'Добавить заявку'})


@login_required
def order_edit(request, pk):
    """Редактировать заявку"""
    order = get_object_or_404(Order, pk=pk, client__business=request.user.businessprofile)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'crm/order_form.html', {'form': form, 'client': order.client, 'title': 'Редактировать заявку'})


@login_required
def order_detail(request, pk):
    """Детали заявки с комментариями"""
    order = get_object_or_404(Order, pk=pk, client__business=request.user.businessprofile)
    comments = order.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.order = order
            comment.save()
            return redirect('order_detail', pk=pk)
    else:
        form = CommentForm()
    
    return render(request, 'crm/order_detail.html', {'order': order, 'comments': comments, 'form': form})


@login_required
def order_delete(request, pk):
    """Удалить заявку"""
    order = get_object_or_404(Order, pk=pk, client__business=request.user.businessprofile)
    client_pk = order.client.pk
    if request.method == 'POST':
        order.delete()
        return redirect('client_detail', pk=client_pk)
    return render(request, 'crm/confirm_delete.html', {'object': order, 'type': 'заявку'})


@login_required
def order_list(request):
    """Список всех заявок"""
    profile = request.user.businessprofile
    orders = Order.objects.filter(client__business=profile)
    
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    
    return render(request, 'crm/order_list.html', {'orders': orders, 'status': status})


@login_required
def export_clients(request):
    """Экспорт клиентов в Excel"""
    profile = request.user.businessprofile
    clients = Client.objects.filter(business=profile)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Клиенты"
    ws.append(['Имя', 'Телефон', 'Заметки', 'Дата добавления'])
    
    for client in clients:
        ws.append([client.name, client.phone, client.notes, client.created_at.strftime('%d.%m.%Y')])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=clients.xlsx'
    wb.save(response)
    return response


@login_required
def export_orders(request):
    """Экспорт заявок в Excel"""
    profile = request.user.businessprofile
    orders = Order.objects.filter(client__business=profile)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Заявки"
    ws.append(['Клиент', 'Телефон', 'Услуга', 'Статус', 'Цена', 'Дата'])
    
    status_map = {'new': 'Новая', 'in_progress': 'В работе', 'done': 'Завершена'}
    
    for order in orders:
        ws.append([
            order.client.name,
            order.client.phone,
            order.service,
            status_map.get(order.status, order.status),
            float(order.price) if order.price else '',
            order.created_at.strftime('%d.%m.%Y')
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response


@login_required
def change_language(request, lang):
    """Смена языка интерфейса"""
    if lang in ['ru', 'tk', 'en']:
        profile = request.user.businessprofile
        profile.language = lang
        profile.save()
        translation.activate(lang)
        request.session['_language'] = lang
        response = redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        response.set_cookie('django_language', lang)
        return response
    return redirect('dashboard')


# ==================== АНАЛИТИКА ====================

@login_required
def analytics(request):
    """Страница аналитики и статистики"""
    profile = request.user.businessprofile
    
    # Основная статистика
    total_clients = Client.objects.filter(business=profile).count()
    total_orders = Order.objects.filter(client__business=profile).count()
    total_revenue = Order.objects.filter(client__business=profile, status='done').aggregate(Sum('price'))['price__sum'] or 0
    
    # Статистика по статусам
    orders_new = Order.objects.filter(client__business=profile, status='new').count()
    orders_in_progress = Order.objects.filter(client__business=profile, status='in_progress').count()
    orders_done = Order.objects.filter(client__business=profile, status='done').count()
    
    # Среднее время выполнения
    completed_orders = Order.objects.filter(
        client__business=profile, 
        status='done', 
        completed_at__isnull=False
    )
    if completed_orders.exists():
        total_days = 0
        for order in completed_orders:
            days = (order.completed_at - order.created_at).days
            total_days += days
        avg_execution_time = round(total_days / completed_orders.count(), 1)
    else:
        avg_execution_time = 0
    
    # Доход по месяцам (последние 6 месяцев)
    months_back = 6
    revenue_by_month = []
    months_labels = []
    
    for i in range(months_back, 0, -1):
        date = now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        if i == 1:
            month_end = now()
        else:
            month_end = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = Order.objects.filter(
            client__business=profile,
            status='done',
            completed_at__range=[month_start, month_end]
        ).aggregate(Sum('price'))['price__sum'] or 0
        
        revenue_by_month.append(float(revenue))
        months_labels.append(month_start.strftime('%b'))
    
    # Распределение по статусам
    status_distribution = {
        'Новые': orders_new,
        'В работе': orders_in_progress,
        'Завершены': orders_done,
    }
    # Сотрудники и заполненность
    employees_count = Employee.objects.filter(business=profile).count()
    max_employees = getattr(profile, 'max_employees', 20) or 20
    try:
        employees_percent = int((employees_count / max_employees) * 100)
    except Exception:
        employees_percent = 0
    
    context = {
        'profile': profile,
        'total_clients': total_clients,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'avg_execution_time': avg_execution_time,
        'orders_new': orders_new,
        'orders_in_progress': orders_in_progress,
        'orders_done': orders_done,
        'employees_count': employees_count,
        'max_employees': max_employees,
        'employees_percent': employees_percent,
        'revenue_by_month': json.dumps(revenue_by_month),
        'months_labels': json.dumps(months_labels),
        'status_distribution': json.dumps(status_distribution),
    }
    
    return render(request, 'crm/analytics.html', context)


# ==================== СОТРУДНИКИ ====================

@login_required
def employee_list(request):
    """Список сотрудников"""
    profile = request.user.businessprofile
    employees = Employee.objects.filter(business=profile)
    return render(request, 'crm/employee_list.html', {'employees': employees})


@login_required
def employee_add(request):
    """Добавить сотрудника"""
    profile = request.user.businessprofile
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        role = request.POST.get('role')
        # Опциональная связь с текущим пользователем (если это новый сотрудник)
        link_user = request.POST.get('link_user')
        
        # Если галочка "это я" - связываем с текущим пользователем
        user_to_link = None
        if link_user:
            # Проверяем, не добавлен ли уже текущий пользователь как сотрудник
            if not Employee.objects.filter(business=profile, user=request.user).exists():
                user_to_link = request.user
        
        Employee.objects.create(
            business=profile,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            role=role,
            user=user_to_link
        )
        return redirect('employee_list')
    
    return render(request, 'crm/employee_form.html', {'title': 'Добавить сотрудника', 'roles': Employee._meta.get_field('role').choices})


@login_required
def employee_edit(request, pk):
    """Редактировать сотрудника"""
    profile = request.user.businessprofile
    employee = get_object_or_404(Employee, pk=pk, business=profile)
    
    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.phone = request.POST.get('phone')
        employee.email = request.POST.get('email')
        employee.role = request.POST.get('role')
        employee.is_active = request.POST.get('is_active') == 'on'
        employee.save()
        return redirect('employee_list')
    
    return render(request, 'crm/employee_form.html', {
        'employee': employee,
        'title': f'Редактировать {employee.first_name}',
        'roles': Employee._meta.get_field('role').choices
    })


@login_required
def employee_delete(request, pk):
    """Удалить сотрудника"""
    profile = request.user.businessprofile
    employee = get_object_or_404(Employee, pk=pk, business=profile)
    
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    
    return render(request, 'crm/confirm_delete.html', {'object': employee, 'type': 'сотрудника'})


# ==================== ЧАТ ====================

@login_required
def chat_list(request):
    """Список чатов"""
    profile = request.user.businessprofile
    try:
        current_employee = Employee.objects.get(business=profile, user=request.user)
    except Employee.DoesNotExist:
        # Если для текущего пользователя нет записи Employee, создаём её автоматически
        current_employee = Employee.objects.create(
            business=profile,
            user=request.user,
            first_name=(request.user.first_name or request.user.username),
            last_name=(request.user.last_name or ''),
            email=(request.user.email or ''),
            role='manager',
            is_active=True,
        )
    
    # Получить все сообщения (входящие и исходящие)
    conversations = Employee.objects.filter(business=profile).exclude(user=request.user)
    
    context = {
        'conversations': conversations,
        'current_employee': current_employee,
    }
    return render(request, 'crm/chat_list.html', context)


@login_required
def chat_detail(request, employee_pk):
    """Детали чата с сотрудником"""
    profile = request.user.businessprofile
    
    try:
        current_employee = Employee.objects.get(business=profile, user=request.user)
    except Employee.DoesNotExist:
        # Автоматически создаём запись сотрудника для текущего пользователя
        current_employee = Employee.objects.create(
            business=profile,
            user=request.user,
            first_name=(request.user.first_name or request.user.username),
            last_name=(request.user.last_name or ''),
            email=(request.user.email or ''),
            role='manager',
            is_active=True,
        )
    
    other_employee = get_object_or_404(Employee, pk=employee_pk, business=profile)
    
    # Получить все сообщения между этими двумя сотрудниками
    messages = Message.objects.filter(
        (Q(sender=current_employee, recipient=other_employee) | Q(sender=other_employee, recipient=current_employee))
    ).order_by('created_at')
    
    # Отметить входящие сообщения как прочитанные
    Message.objects.filter(sender=other_employee, recipient=current_employee, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text.strip():
            Message.objects.create(
                sender=current_employee,
                recipient=other_employee,
                text=text
            )
            return redirect('chat_detail', employee_pk=employee_pk)
    
    context = {
        'current_employee': current_employee,
        'other_employee': other_employee,
        'messages': messages,
    }
    return render(request, 'crm/chat_detail.html', context)

# ==================== ВРЕМЯ РАБОТЫ ====================

@login_required
def start_work(request):
    """Начать рабочий день"""
    try:
        business = request.user.businessprofile
        # Пытаемся найти сотрудника по user
        try:
            employee = business.employees.get(user=request.user)
        except Employee.DoesNotExist:
            # Если не найдено, возвращаемся назад с ошибкой
            from django.contrib import messages
            messages.error(request, 'Вы не добавлены как сотрудник компании')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        # Проверяем, нет ли активной сессии работы
        active_log = employee.work_logs.filter(end_time__isnull=True).first()
        
        if not active_log:
            WorkLog.objects.create(
                employee=employee,
                start_time=now()
            )
            from django.contrib import messages
            messages.success(request, f'Рабочий день начат! ✓')
        else:
            from django.contrib import messages
            messages.warning(request, 'У вас уже есть активная рабочая сессия')
            
    except BusinessProfile.DoesNotExist:
        pass
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def end_work(request):
    """Завершить рабочий день"""
    try:
        business = request.user.businessprofile
        # Пытаемся найти сотрудника по user
        try:
            employee = business.employees.get(user=request.user)
        except Employee.DoesNotExist:
            # Если не найдено, возвращаемся назад с ошибкой
            from django.contrib import messages
            messages.error(request, 'Вы не добавлены как сотрудник компании')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        # Находим активную сессию работы
        active_log = employee.work_logs.filter(end_time__isnull=True).first()
        
        if active_log:
            active_log.end_time = now()
            active_log.save()
            from django.contrib import messages
            messages.success(request, f'Рабочий день завершён! ✓')
        else:
            from django.contrib import messages
            messages.warning(request, 'Нет активной рабочей сессии для завершения')
            
    except BusinessProfile.DoesNotExist:
        pass
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def work_time_report(request):
    """Отчёт по времени работы сотрудников"""
    business = request.user.businessprofile
    
    # Проверяем подписку
    if not business.is_subscription_valid():
        return redirect('blocked')
    
    # Только админ может смотреть все отчёты
    try:
        employee = business.employees.get(user=request.user)
        if employee.role != 'admin':
            return redirect('dashboard')
    except Employee.DoesNotExist:
        return redirect('dashboard')
    
    employees = business.employees.all()
    
    # Получаем дату фильтрации (по умолчанию сегодня)
    from datetime import date
    filter_date = request.GET.get('date')
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
        except:
            filter_date = date.today()
    else:
        filter_date = date.today()
    
    # Получаем работу за выбранную дату
    work_logs = WorkLog.objects.filter(
        employee__business=business,
        start_time__date=filter_date
    ).select_related('employee').order_by('-start_time')
    
    # Подсчитываем общее время работы по сотрудникам
    employee_work_time = {}
    for log in work_logs:
        emp_id = log.employee.id
        if emp_id not in employee_work_time:
            employee_work_time[emp_id] = timedelta()
        employee_work_time[emp_id] += log.duration
    
    context = {
        'employees': employees,
        'work_logs': work_logs,
        'employee_work_time': employee_work_time,
        'filter_date': filter_date,
    }
    
    return render(request, 'crm/work_time_report.html', context)


@login_required
def employee_work_time(request, employee_pk):
    """История времени работы конкретного сотрудника"""
    business = request.user.businessprofile
    
    # Проверяем подписку
    if not business.is_subscription_valid():
        return redirect('blocked')
    
    employee = get_object_or_404(Employee, pk=employee_pk, business=business)
    
    # Только сам сотрудник или админ могут смотреть
    try:
        current_employee = business.employees.get(user=request.user)
        if current_employee.role != 'admin' and current_employee != employee:
            return redirect('dashboard')
    except Employee.DoesNotExist:
        return redirect('dashboard')
    
    # Получаем фильтрацию по месяцу
    from datetime import date
    filter_month = request.GET.get('month')
    if filter_month:
        try:
            year, month = filter_month.split('-')
            filter_date = date(int(year), int(month), 1)
        except:
            filter_date = date.today()
    else:
        filter_date = date.today()
    
    # Получаем логи работы
    start_of_month = filter_date.replace(day=1)
    if filter_date.month == 12:
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)
    
    work_logs = employee.work_logs.filter(
        start_time__date__gte=start_of_month,
        start_time__date__lte=end_of_month
    ).order_by('-start_time')
    
    # Подсчитываем общее время работы в месяце
    total_time = timedelta()
    for log in work_logs:
        total_time += log.duration
    
    context = {
        'employee': employee,
        'work_logs': work_logs,
        'total_time': total_time,
        'filter_date': filter_date,
    }
    
    return render(request, 'crm/employee_work_time.html', context)