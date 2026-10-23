from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import drive


class DriveListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Lista arquivos da pasta do Drive', responses={200: dict})
    def get(self, request):
        return Response(drive.listar_arquivos())


class DriveDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Baixa um arquivo do Drive', responses={200: bytes})
    def get(self, request, arquivo_id):
        try:
            nome, mime, conteudo = drive.baixar_arquivo(arquivo_id)
        except PermissionError as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            raise NotFound(str(exc))
        resp = HttpResponse(conteudo, content_type=mime)
        resp['Content-Disposition'] = f'attachment; filename="{nome}"'
        return resp
