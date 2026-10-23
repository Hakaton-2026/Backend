from rest_framework.viewsets import ModelViewSet

from core.models import Projeto
from core.serializers import ProjetoSerializer


class ProjetoViewSet(ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer
