from rest_framework.views import ModelViewSet

from core.models import Nota
from core.serializers import NotaSerializer

class NotaViewSet(ModelViewSet):
    queryset = Nota.objects.all().order_by('-id')
    serializer_class = NotaSerializer
