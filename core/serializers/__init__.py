from .user import (
    ChangePasswordSerializer,
    EmailVerifiedTokenObtainPairSerializer,
    ResendCodeSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VerifyEmailSerializer
)
from .tarefa import TarefaCreateUpdateSerializer, TarefaListSerializer, TarefaRetrieveSerializer
from .comentario import ComentarioSerializer
from .projeto import ProjetoCreateUpdateSerializer, ProjetoListSerializer, ProjetoRetrieveSerializer