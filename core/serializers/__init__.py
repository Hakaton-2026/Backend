from .user import (
    ChangePasswordSerializer,
    EmailVerifiedTokenObtainPairSerializer,
    ResendCodeSerializer,
    UserRegistrationSerializer,
    UserResumoSerializer,
    UserSerializer,
    VerifyEmailSerializer
)

from .comentario import ComentarioSerializer
from .checklist_item import ChecklistItemSerializer
from .material_apoio import MaterialApoioSerializer
from .tarefa import (
    TarefaAninhadaSerializer,
    TarefaCreateUpdateSerializer,
    TarefaListSerializer,
    TarefaRetrieveSerializer,
)
from .nota import NotaSerializer
from .projeto import (
    ProjetoCreateUpdateSerializer,
    ProjetoListSerializer,
    ProjetoMembroSerializer,
    ProjetoRetrieveSerializer,
)