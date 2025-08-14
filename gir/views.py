from django.shortcuts import render, redirect
from .models import FrontendUser
from django.contrib import messages

def frontend_login(request):
    """Форма входа для пользователей фронтенда"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = FrontendUser.objects.get(username=username, is_active=True)
            if user.check_password(password):
                # Создаем сессию для фронтенд пользователя
                request.session['frontend_user_id'] = user.id
                request.session['frontend_username'] = user.username
                return redirect('dashboard')
            else:
                messages.error(request, 'Неправильний логін або пароль')
        except FrontendUser.DoesNotExist:
            messages.error(request, 'Неправильний логін або пароль')
    
    return render(request, 'gir/login.html')

def frontend_logout(request):
    """Выход для пользователей фронтенда"""
    if 'frontend_user_id' in request.session:
        del request.session['frontend_user_id']
        del request.session['frontend_username']
    return redirect('home')

def get_frontend_user(request):
    """Получаем текущего фронтенд пользователя из сессии"""
    if 'frontend_user_id' in request.session:
        try:
            return FrontendUser.objects.get(id=request.session['frontend_user_id'], is_active=True)
        except FrontendUser.DoesNotExist:
            # Очищаем сессию если пользователь не найден
            del request.session['frontend_user_id']
            del request.session['frontend_username']
    return None

def frontend_login_required(view_func):
    """Декоратор для проверки входа фронтенд пользователя"""
    def wrapper(request, *args, **kwargs):
        if get_frontend_user(request):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')
    return wrapper

@frontend_login_required
def dashboard(request):
    """Dashboard для фронтенд пользователей"""
    frontend_user = get_frontend_user(request)
    return render(request, 'gir/dashboard.html', {'frontend_user': frontend_user})

def home(request):
    """Главная страница - форма входа для фронтенда"""
    # Проверяем, есть ли активная сессия фронтенд пользователя
    if get_frontend_user(request):
        return redirect('dashboard')
    return render(request, 'gir/login.html')
