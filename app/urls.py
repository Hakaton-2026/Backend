from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from core.views import (
    ComentarioViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    ProjetoViewSet,
    ResendVerificationCodeView,
    TarefaViewSet,
    UserRegistrationView,
    UserViewSet,
    VerifyEmailView,
)
from core.views.drive import DriveDownloadView, DriveListView
from uploader.router import router as uploader_router

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuarios')
router.register(r'tarefas', TarefaViewSet, basename='tarefas')
router.register(r'comentarios', ComentarioViewSet, basename='comentarios')
router.register(r'projetos', ProjetoViewSet, basename='projetos')


urlpatterns = [
    path('accounts/', include('allauth.urls')),

    path('admin/', admin.site.urls),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/doc/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),

    # Upload de arquivos
    path('api/media/', include(uploader_router.urls)),

    # Google Drive (somente leitura)
    path('api/drive/', DriveListView.as_view(), name='drive_list'),
    path(
        'api/drive/<str:arquivo_id>/',
        DriveDownloadView.as_view(),
        name='drive_download',
    ),

    # Autenticação JWT
    path(
        'api/token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path(
        'api/token/refresh/',
        CustomTokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path(
        'api/token/verify/',
        CustomTokenVerifyView.as_view(),
        name='token_verify',
    ),

    # Cadastro e verificação do e-mail
    path(
        'api/registro/',
        UserRegistrationView.as_view(),
        name='user_registration',
    ),
    path(
        'api/verificar-email/',
        VerifyEmailView.as_view(),
        name='verify_email',
    ),
    path(
        'api/reenviar-codigo/',
        ResendVerificationCodeView.as_view(),
        name='resend_code',
    ),

    # Rotas de usuário
    path('api/', include(router.urls)),
]

urlpatterns += static(
    settings.MEDIA_ENDPOINT,
    document_root=settings.MEDIA_ROOT,
)
