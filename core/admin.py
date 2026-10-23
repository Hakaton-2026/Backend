from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import Tarefa, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Personaliza a administração das contas de usuário."""

    ordering = ('-created_at', 'email')

    list_display = (
        'email',
        'name',
        'theme',
        'email_verified',
        'is_active',
        'is_staff',
        'created_at',
        'last_login',
        'get_profile_photo_preview',
    )

    list_display_links = ('email',)

    list_filter = (
        'email_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'theme',
    )

    search_fields = (
        'email',
        'name',
    )

    date_hierarchy = 'created_at'

    list_per_page = 25

    list_select_related = ('profile_photo',)

    filter_horizontal = (
        'groups',
        'user_permissions',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                )
            },
        ),
        (
            _('Informações pessoais'),
            {
                'fields': (
                    'name',
                    'theme',
                    'profile_photo',
                    'get_profile_photo_preview',
                )
            },
        ),
        (
            _('Verificação de e-mail'),
            {
                'fields': (
                    'email_verified',
                    'verification_code',
                    'verification_code_created_at',
                    'verification_attempts',
                )
            },
        ),
        (
            _('Permissões e acesso'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            },
        ),
        (
            _('Grupos'),
            {
                'fields': (
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            _('Datas importantes'),
            {
                'fields': (
                    'last_login',
                    'created_at',
                )
            },
        ),
    )

    readonly_fields = (
        'last_login',
        'created_at',
        'verification_code',
        'verification_code_created_at',
        'verification_attempts',
        'get_profile_photo_preview',
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'name',
                    'password1',
                    'password2',
                    'theme',
                    'profile_photo',
                    'get_profile_photo_preview',
                    'email_verified',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )

    @admin.display(description='Foto de perfil')
    def get_profile_photo_preview(self, obj):
        """Exibe a imagem de perfil do usuário no painel administrativo."""

        if not obj or not obj.profile_photo:
            return 'Sem foto de perfil'

        try:
            url = obj.profile_photo.url
        except (ValueError, OSError, AttributeError):
            return 'Imagem indisponível'

        if not url:
            return 'Sem foto de perfil'

        return format_html(
            (
                '<img src="{}" alt="Foto de perfil" '
                'style="width: 80px; height: 80px; '
                'object-fit: cover; border-radius: 8px;" />'
            ),
            url,
        )


@admin.register(Tarefa)
class TarefasAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prazoInicio', 'prazoFim')
    search_fields = ('titulo', 'prazoInicio', 'prazoFim')
    list_filter = ('titulo',)
    ordering = ('titulo', 'prazoInicio', 'prazoFim')
    list_per_page = 10
