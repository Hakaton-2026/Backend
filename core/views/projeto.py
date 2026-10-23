from rest_framework.viewsets import ModelViewSet

from core.models import Projeto
from core.serializers import ProjetoCreateUpdateSerializer, ProjetoListSerializer, ProjetoRetrieveSerializer


class ProjetoViewSet(ModelViewSet):
    queryset = Projeto.objects.all()

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return ProjetoCreateUpdateSerializer
        if self.action == 'list':
            return ProjetoListSerializer
        return ProjetoRetrieveSerializer
