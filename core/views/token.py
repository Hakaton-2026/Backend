from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenVerifySerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.serializers.user import EmailVerifiedTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        summary='Obter token JWT',
        description=(
            'Autentica com e-mail e senha. '
            'Retorna access token e refresh token.'
        ),
        request=EmailVerifiedTokenObtainPairSerializer,
        responses={200: EmailVerifiedTokenObtainPairSerializer, 401: None},
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    # Não permite login antes da verificação do e-mail.
    serializer_class = EmailVerifiedTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        summary='Atualizar token JWT',
        description='Retorna um novo access token a partir do refresh token.',
        request=TokenRefreshSerializer,
        responses={200: TokenRefreshSerializer, 401: None},
    )
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary='Verificar token JWT',
        description='Verifica se um token JWT é válido.',
        request=TokenVerifySerializer,
        responses={200: None, 401: None},
    )
)
class CustomTokenVerifyView(TokenVerifyView):
    pass
