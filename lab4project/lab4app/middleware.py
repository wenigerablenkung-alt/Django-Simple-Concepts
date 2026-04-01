import time
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("RequestLoggingMiddleware initialized")

    def __call__(self, request):
        start_time = time.time()
        user = request.user.username if request.user.is_authenticated else "anonymous"
        print(f"[{request.method}] {request.path} | User: {user}")
        response = self.get_response(request)
        duration_ms = (time.time() - start_time) * 1000
        print(f"[{response.status_code}] {request.path} | {duration_ms:.1f}ms")
        response["X-Processing-Time"] = f"{duration_ms:.1f}ms"

        return response


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(
            f"Unhandled exception on {request.path}: {type(exception).__name__}: {exception}",
            exc_info=True,
        )

        if request.path.startswith("/api/"):
            return JsonResponse(
                {"error": "Internal server error", "detail": str(exception)}, status=500
            )
        return None


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["X-Powered-By"] = "Django Learning App"

        return response


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        if getattr(settings, "MAINTENANCE_MODE", False):
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)

            from django.http import HttpResponse

            return HttpResponse(
                "<h1>Under Maintenance</h1><p>We'll be back shortly!</p>", status=503
            )

        return self.get_response(request)
