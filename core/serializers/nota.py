from rest_framework.serializers import ModelSerializer

from core.models import Nota


class NotaSerializer(ModelSerializer):
    class Meta:
        model = Nota
        fields = '__all__'
