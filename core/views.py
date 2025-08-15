from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from io import StringIO

def health(request):
    return JsonResponse({"ok": True})

def migrations_status(request):
    """Проверка состояния миграций"""
    try:
        # Захватываем вывод команды showmigrations
        output = StringIO()
        call_command('showmigrations', stdout=output)
        migrations_output = output.getvalue()
        
        # Парсим вывод
        migrations = {}
        current_app = None
        
        for line in migrations_output.split('\n'):
            line = line.strip()
            if line and not line.startswith('['):
                if line.endswith(':'):
                    current_app = line[:-1]
                    migrations[current_app] = []
                elif current_app and line.startswith('['):
                    # [X] означает применена, [ ] означает не применена
                    status = 'applied' if line.startswith('[X]') else 'not_applied'
                    migration_name = line[4:]  # Убираем [X] или [ ]
                    migrations[current_app].append({
                        'name': migration_name,
                        'status': status
                    })
        
        return JsonResponse({
            "status": "success",
            "migrations": migrations
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        }, status=500)
