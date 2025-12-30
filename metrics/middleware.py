import time

from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Gauge, Histogram
from starlette.types import ASGIApp

labels = ["app_name", "method", "endpoint", "http_status"]

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    labels
)

RESPONSE_TIME = Histogram(
    "http_response_time",
    "Response time",
    labels,
    buckets=(
        0.05, 0.1, 0.2, 0.3, 0.5,
        0.75, 1.0, 1.5, 2.0, 3.0, 5.0
    )
)


# : Request
def get_route_path(request) -> str:
    for route in request.app.routes:
        if isinstance(route, APIRoute) and route.matches(request)[0].value == 2:
            return route.path
    return "unknown"


class MetricsMiddleware(BaseHTTPMiddleware):

    # def __init__(self, app_name, app: ASGIApp):
    #     BaseHTTPMiddleware.__init__(self, app)
    #     self.app_name = app_name

    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        path = get_route_path(request)
        app_name = "smmetrics"
        REQUEST_COUNT.labels(
            # app_name=self.app_name,
            app_name=app_name,
            method=request.method,
            endpoint=path,
            http_status=str(response.status_code)
        ).inc()

        RESPONSE_TIME.labels(
            # app_name=self.app_name,
            app_name=app_name,
            method=request.method,
            endpoint=path,
            http_status=str(response.status_code)
        ).observe(duration)

        return response
