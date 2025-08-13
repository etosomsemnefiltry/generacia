from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def health(request):
    return JsonResponse({"ok": True})
