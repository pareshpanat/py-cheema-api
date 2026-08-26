from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("py-cheema-api")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .app import APIRouter, Cheema
from .config import CheemaSettings
from .deps import (
    Body,
    ClassDepends,
    Cookie,
    DependencyGroup,
    Depends,
    File,
    Form,
    Header,
    Host,
    Query,
    Security,
    dependency_group,
)
from .errors import HTTPError
from .extensions import (
    CheemaExtension,
    ExtensionRegistry,
    register_extension_hook,
    run_extension_hooks,
)
from .jobs import (
    CeleryQueueAdapter,
    InMemoryJobQueue,
    JobRecord,
    RedisQueueAdapter,
    RetryPolicy,
    RQQueueAdapter,
)
from .lifespan import app_state_dependency, get_app_state
from .middleware import (
    CompressionMiddleware,
    CORSMiddleware,
    CSRFMiddleware,
    GZipMiddleware,
    HTTPSRedirectMiddleware,
    MemorySessionBackend,
    ProxyHeadersMiddleware,
    RateLimitMiddleware,
    ResponseCacheMiddleware,
    SessionMiddleware,
    TrustedHostMiddleware,
)
from .models import Model, field, field_validator, model_validator, type_validator
from .observability import (
    LogEvent,
    MetricEvent,
    MetricsMiddleware,
    OpenTelemetryTracingHook,
    PrometheusMiddleware,
    RequestIDMiddleware,
    StructuredLoggingMiddleware,
    TracingMiddleware,
    get_request_id,
    set_request_id,
)
from .request import (
    ConnectionManager,
    Request,
    UploadFile,
    WebSocket,
    normalize_ws_close_code,
    ws_close_reason,
)
from .response import (
    BackgroundTask,
    EventSourceResponse,
    FileResponse,
    HTMLResponse,
    JSONResponse,
    NegotiatedResponse,
    RedirectResponse,
    Response,
    SSEEvent,
    StreamingResponse,
    TextResponse,
    build_cache_control,
    encode_sse_event,
    negotiate_content_type,
    register_json_encoder,
    with_cache_headers,
)
from .security import (
    JWKSCache,
    api_key_auth,
    bearer_auth,
    csrf_protect,
    csrf_token,
    jwt_auth,
    oauth2_authorization_code,
    oauth2_bearer,
    oauth2_client_credentials,
    websocket_jwt_auth,
    websocket_token_auth,
)
from .testing import AsyncTestClient, TestClient, TestResponse, WebSocketTestSession

__all__ = ["__version__","Cheema","APIRouter","CheemaSettings","Request","WebSocket","UploadFile","ConnectionManager","normalize_ws_close_code","ws_close_reason","Response","JSONResponse","TextResponse","HTMLResponse","RedirectResponse","StreamingResponse","EventSourceResponse","SSEEvent","encode_sse_event","negotiate_content_type","NegotiatedResponse","build_cache_control","with_cache_headers","FileResponse","BackgroundTask","register_json_encoder","HTTPError","Depends","Security","ClassDepends","DependencyGroup","dependency_group","Query","Header","Cookie","Form","File","Host","Body","Model","field","field_validator","model_validator","type_validator","api_key_auth","bearer_auth","jwt_auth","oauth2_bearer","oauth2_authorization_code","oauth2_client_credentials","csrf_token","csrf_protect","JWKSCache","websocket_token_auth","websocket_jwt_auth","CORSMiddleware","GZipMiddleware","CompressionMiddleware","RateLimitMiddleware","ResponseCacheMiddleware","TrustedHostMiddleware","SessionMiddleware","CSRFMiddleware","HTTPSRedirectMiddleware","ProxyHeadersMiddleware","MemorySessionBackend","RequestIDMiddleware","StructuredLoggingMiddleware","MetricsMiddleware","PrometheusMiddleware","TracingMiddleware","OpenTelemetryTracingHook","LogEvent","MetricEvent","get_request_id","set_request_id","TestClient","TestResponse","AsyncTestClient","WebSocketTestSession","app_state_dependency","get_app_state","InMemoryJobQueue","RetryPolicy","JobRecord","CeleryQueueAdapter","RQQueueAdapter","RedisQueueAdapter","CheemaExtension","ExtensionRegistry","register_extension_hook","run_extension_hooks"]
