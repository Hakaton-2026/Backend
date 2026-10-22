import os

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User
from core.serializers import (
    ChangePasswordSerializer,
    ResendCodeSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

EXPOSE_VERIFICATION_CODE = os.getenv(
    'EXPOSE_VERIFICATION_CODE',
    'False',
).strip().lower() in {'1', 'true', 'yes', 'on'}

MAX_VERIFICATION_ATTEMPTS = 5


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Permite que o usuário consulte somente a própria conta."""
        if (
            not self.request.user
            or not self.request.user.is_authenticated
        ):
            return User.objects.none()

        return User.objects.filter(
            pk=self.request.user.pk
        ).order_by('id')

    def create(self, request, *args, **kwargs):
        """O cadastro deve utilizar o endpoint específico de registro."""
        raise MethodNotAllowed(
            'POST',
            detail='Use /api/registro/ para criar uma conta.',
        )

    def destroy(self, request, *args, **kwargs):
        """Não permite excluir uma conta por este endpoint."""
        raise MethodNotAllowed(
            'DELETE',
            detail='A exclusão de contas não está disponível por este endpoint.',
        )

    @extend_schema(
        summary='Dados do usuário autenticado',
        description='Retorna ou atualiza os dados da própria conta.',
        responses={200: UserSerializer, 401: None},
    )
    @action(
        detail=False,
        methods=['get', 'patch', 'put'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        serializer = UserSerializer(
            user,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def buscar(self, request):
        """Busca usuários por nome ou e-mail, sem incluir a própria conta."""
        termo = request.query_params.get('q', '')

        usuarios = User.objects.filter(
            Q(name__icontains=termo)
            | Q(email__icontains=termo)
        ).exclude(
            id=request.user.id
        )[:20]

        return Response(
            UserSerializer(usuarios, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Alterar senha',
        description='Altera a senha após validar a senha atual.',
        request=ChangePasswordSerializer,
        responses={200: None, 400: None},
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Senha alterada com sucesso.'},
            status=status.HTTP_200_OK,
        )


class UserRegistrationView(CreateAPIView):
    """Registra uma conta e inicia a verificação do e-mail."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        codigo_teste = None

        if EXPOSE_VERIFICATION_CODE:
            # Somente no modo de teste:
            # gera o código sem tentar enviar um e-mail.
            codigo_teste = user.generate_verification_code()
        else:
            # Com o modo de teste desativado, envia o e-mail normalmente.
            user.send_verification_email()

        dados = dict(serializer.data)

        if codigo_teste is not None:
            dados['debug_verification_code'] = codigo_teste

        return Response(
            dados,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class VerifyEmailView(APIView):
    """Confirma o código e retorna tokens JWT."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyEmailSerializer,
        responses={200: None, 400: None, 404: None},
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        codigo = serializer.validated_data['codigo']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.email_verified:
            return Response(
                {'detail': 'E-mail já verificado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
            return Response(
                {
                    'detail': (
                        'Muitas tentativas. Solicite um novo código.'
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if user.is_code_expired():
            return Response(
                {'detail': 'Código expirado. Solicite um novo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.verification_code != codigo:
            user.verification_attempts += 1
            user.save(update_fields=['verification_attempts'])

            return Response(
                {'detail': 'Código inválido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.verification_code = None

        user.save(
            update_fields=['email_verified', 'verification_code'],
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'detail': 'E-mail verificado com sucesso!',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationCodeView(APIView):
    """Reenvia o código de verificação ou o devolve no modo de teste."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=ResendCodeSerializer,
        responses={200: None, 400: None, 404: None},
    )
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.email_verified:
            return Response(
                {'detail': 'E-mail já verificado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if EXPOSE_VERIFICATION_CODE:
            codigo = user.generate_verification_code()

            return Response(
                {
                    'detail': 'Código gerado no modo de teste.',
                    'debug_verification_code': codigo,
                },
                status=status.HTTP_200_OK,
            )

        user.send_verification_email()

        return Response(
            {'detail': 'Novo código enviado.'},
            status=status.HTTP_200_OK,
        )
