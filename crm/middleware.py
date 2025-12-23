from django.utils import translation
from django.shortcuts import redirect
from django.urls import reverse


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                lang = request.user.businessprofile.language
                translation.activate(lang)
                request.LANGUAGE_CODE = lang
            except:
                pass
        response = self.get_response(request)
        return response


class SubscriptionCheckMiddleware:
    """Проверка активности подписки"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пропускаем для неавторизованных и админов
        allowed_paths = ['/login/', '/register/', '/logout/', '/blocked/', '/admin/']
        
        if any(request.path.startswith(p) for p in allowed_paths):
            return self.get_response(request)
        
        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                profile = request.user.businessprofile
                if not profile.is_subscription_valid():
                    return redirect('blocked')
            except:
                pass
        
        return self.get_response(request)

