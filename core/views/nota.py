from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from core.models import Nota
from core.serializers import NotaSerializer


class NotaViewSet(ModelViewSet):
    serializer_class = NotaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Nota.objects.filter(
            user=self.request.user
        ).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
