import os

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


class GoogleLoginView(APIView):
    """Troca o code do Google por um par de tokens JWT da aplicação."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        if not code or not redirect_uri:
            return Response(
                {'detail': 'code e redirect_uri são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            return Response(
                {'detail': 'Login com Google não configurado no servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        flow = Flow.from_client_config(
            {
                'web': {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                }
            },
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )

        try:
            flow.fetch_token(code=code)
            info = id_token.verify_oauth2_token(
                flow.credentials.id_token,
                google_requests.Request(),
                client_id,
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível validar o login com o Google.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not info.get('email_verified'):
            return Response(
                {'detail': 'O e-mail do Google não está verificado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = info['email'].lower()
        user = User.objects.filter(email=email).first()

        if user is None:
            user = User.objects.create_user(
                email=email,
                name=info.get('name') or email.split('@')[0],
                password=None,
            )

        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        )