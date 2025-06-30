from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from pyramid.view import view_config
from pyramid.response import Response

# Ejemplo de métrica personalizada
REQUEST_COUNT = Counter('worq_http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])

@view_config(route_name='metrics')
def metrics_view(request):
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)