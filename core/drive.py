import io
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

BASE_DIR = Path(__file__).resolve().parents[1]

# Arquivos nativos do Google não baixam direto: precisam ser exportados.
EXPORT_MIME = {
    'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
    'application/vnd.google-apps.spreadsheet': (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xlsx',
    ),
    'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
}

PASTA_MIME = 'application/vnd.google-apps.folder'


def _credentials():
    info = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')  # produção: conteúdo do JSON
    if info:
        return service_account.Credentials.from_service_account_info(
            json.loads(info), scopes=SCOPES
        )

    caminho = Path(
        os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'segredos/service-account.json')
    )
    if not caminho.is_absolute():
        caminho = BASE_DIR / caminho
    return service_account.Credentials.from_service_account_file(
        str(caminho), scopes=SCOPES
    )


def _drive():
    return build('drive', 'v3', credentials=_credentials(), cache_discovery=False)


def _pasta_padrao():
    return os.environ['GOOGLE_DRIVE_FOLDER_ID']


def listar_arquivos(pasta_id=None, limite=50):
    """Lista os arquivos de uma pasta (padrão: GOOGLE_DRIVE_FOLDER_ID)."""
    pasta_id = pasta_id or _pasta_padrao()
    resp = (
        _drive()
        .files()
        .list(
            q=f"'{pasta_id}' in parents and trashed = false",
            pageSize=limite,
            fields='files(id, name, mimeType, size, modifiedTime)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    return resp.get('files', [])


def _pertence_a_pasta(drive, arquivo_id, pasta_id):
    """Confere se o arquivo está diretamente na pasta configurada."""
    meta = (
        drive.files()
        .get(fileId=arquivo_id, fields='parents', supportsAllDrives=True)
        .execute()
    )
    return pasta_id in meta.get('parents', [])


def baixar_arquivo(arquivo_id):
    """Baixa um arquivo da pasta configurada. Retorna (nome, mime, bytes)."""
    drive = _drive()

    if not _pertence_a_pasta(drive, arquivo_id, _pasta_padrao()):
        raise PermissionError('Arquivo fora da pasta configurada.')

    meta = (
        drive.files()
        .get(fileId=arquivo_id, fields='name, mimeType', supportsAllDrives=True)
        .execute()
    )
    nome, mime = meta['name'], meta['mimeType']

    if mime == PASTA_MIME:
        raise ValueError('Não é possível baixar uma pasta.')

    if mime in EXPORT_MIME:
        mime_saida, extensao = EXPORT_MIME[mime]
        req = drive.files().export_media(fileId=arquivo_id, mimeType=mime_saida)
        if not nome.lower().endswith(extensao):
            nome += extensao
        mime = mime_saida
    else:
        req = drive.files().get_media(fileId=arquivo_id, supportsAllDrives=True)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, req)
    pronto = False
    while not pronto:
        _, pronto = downloader.next_chunk()

    return nome, mime, buf.getvalue()
