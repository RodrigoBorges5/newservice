from django.http import JsonResponse

EXCLUDED_PATHS = [
    "/service/",      
]

class UserHeaderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in EXCLUDED_PATHS:
            return self.get_response(request)
         
        user_id = request.headers.get("X-User-ID")
        role = request.headers.get("X-User-Role", "user")

        if not user_id:
            return JsonResponse(
                {"detail": "Header X-User-ID em falta"},
                status=401
            )
        
        request.user_id = user_id
        request.role = role

        return self.get_response(request)
