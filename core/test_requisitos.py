from rest_framework.test import APIClient, APITestCase

from core.models import User


def novo(email):
    return User.objects.create_user(
        email=email,
        password='senha12345',
        name=email.split('@')[0],
        email_verified=True,
    )


def cliente(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


class RequisitosTest(APITestCase):
    def setUp(self):
        self.a, self.b, self.c, self.d = (
            novo(f'{n}@x.com') for n in 'abcd'
        )
        self.ca, self.cb, self.cc, self.cd = map(
            cliente,
            (self.a, self.b, self.c, self.d),
        )

        r = self.ca.post(
            '/api/projetos/',
            {'nome': 'P1', 'descricao': 'desc'},
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.pid = r.data['id']
        self.assertEqual(r.data['meu_papel'], 'proprietario')

        r = self.ca.post(
            f'/api/projetos/{self.pid}/membros/',
            {'usuario': self.b.id, 'papel': 'editor'},
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.mb = r.data['id']
        self.assertEqual(r.data['usuario']['email'], 'b@x.com')

        r = self.ca.post(
            f'/api/projetos/{self.pid}/membros/',
            {'usuario': self.c.id, 'papel': 'visualizador'},
            format='json',
        )
        self.mc = r.data['id']

    def tarefa(self, cli, **extra):
        dados = {
            'titulo': 'T',
            'prioridade': 2,
            'prazoInicio': '2026-10-24',
            'prazoFim': '2026-10-30',
            'projeto': self.pid,
        }
        dados.update(extra)

        return cli.post('/api/tarefas/', dados, format='json')

    def test_autenticacao_e_acesso(self):
        self.assertEqual(
            APIClient().get('/api/projetos/').status_code,
            401,
        )
        self.assertEqual(
            APIClient().get('/api/tarefas/').status_code,
            401,
        )
        self.assertEqual(
            self.cd.get(f'/api/projetos/{self.pid}/').status_code,
            404,
        )
        self.assertEqual(
            self.cd.get('/api/projetos/').data['results'],
            [],
        )
        self.assertEqual(
            self.cc.get(f'/api/projetos/{self.pid}/').status_code,
            200,
        )
        self.assertEqual(
            self.cc.get(f'/api/projetos/{self.pid}/').data['meu_papel'],
            'visualizador',
        )

    def test_projeto_editar_e_participantes(self):
        self.assertEqual(
            self.cb.patch(
                f'/api/projetos/{self.pid}/',
                {'nome': 'P1b'},
                format='json',
            ).status_code,
            200,
        )
        self.assertEqual(
            self.cc.patch(
                f'/api/projetos/{self.pid}/',
                {'nome': 'X'},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(
            self.cb.post(
                f'/api/projetos/{self.pid}/membros/',
                {'usuario': self.d.id, 'papel': 'editor'},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(
            self.ca.post(
                f'/api/projetos/{self.pid}/membros/',
                {'usuario': self.b.id, 'papel': 'editor'},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.ca.post(
                f'/api/projetos/{self.pid}/membros/',
                {'usuario': self.a.id, 'papel': 'editor'},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.ca.patch(
                f'/api/projetos/{self.pid}/membros/{self.mc}/',
                {'papel': 'editor'},
                format='json',
            ).data['papel'],
            'editor',
        )
        self.assertEqual(
            self.cb.delete(f'/api/projetos/{self.pid}/').status_code,
            403,
        )

        # Ao remover o responsável, as tarefas passam para o proprietário.
        tarefa_c = self.tarefa(self.ca, user=self.c.id)
        self.assertEqual(tarefa_c.status_code, 201, tarefa_c.data)

        self.assertEqual(
            self.ca.delete(
                f'/api/projetos/{self.pid}/membros/{self.mc}/'
            ).status_code,
            204,
        )

        tarefa_reatribuida = self.ca.get(
            f"/api/tarefas/{tarefa_c.data['id']}/"
        )
        self.assertEqual(
            tarefa_reatribuida.status_code,
            200,
            tarefa_reatribuida.data,
        )
        self.assertEqual(
            tarefa_reatribuida.data['user'],
            self.a.id,
        )
        self.assertEqual(
            self.cc.get(f'/api/projetos/{self.pid}/').status_code,
            404,
        )
        self.assertEqual(
            len(
                self.ca.get(
                    f'/api/projetos/{self.pid}/membros/'
                ).data
            ),
            1,
        )

    def test_tarefas(self):
        r = self.tarefa(self.cb, user=self.b.id)
        self.assertEqual(r.status_code, 201, r.data)
        tid = r.data['id']

        # Responsável fora do projeto.
        self.assertEqual(
            self.tarefa(self.ca, user=self.d.id).status_code,
            400,
        )

        # Visualizador e usuário externo não podem criar tarefas.
        self.assertEqual(
            self.tarefa(self.cc, user=self.c.id).status_code,
            400,
        )
        self.assertEqual(
            self.tarefa(self.cd, user=self.d.id).status_code,
            400,
        )

        # Responsável padrão = usuário autenticado.
        self.assertEqual(
            self.tarefa(self.ca).data['user'],
            self.a.id,
        )

        # Editar e excluir.
        self.assertEqual(
            self.cc.patch(
                f'/api/tarefas/{tid}/',
                {'titulo': 'x'},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(
            self.ca.patch(
                f'/api/tarefas/{tid}/',
                {'titulo': 'novo', 'user': self.a.id},
                format='json',
            ).status_code,
            200,
        )
        self.assertEqual(
            self.ca.patch(
                f'/api/tarefas/{tid}/',
                {'user': self.d.id},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.cd.get(f'/api/tarefas/{tid}/').status_code,
            404,
        )
        self.assertEqual(
            self.cd.delete(f'/api/tarefas/{tid}/').status_code,
            404,
        )
        self.assertEqual(
            self.cc.get(f'/api/tarefas/{tid}/').status_code,
            200,
        )
        self.assertEqual(
            self.ca.delete(f'/api/tarefas/{tid}/').status_code,
            204,
        )

        # Prazo invertido.
        self.assertEqual(
            self.tarefa(
                self.ca,
                prazoFim='2026-01-01',
            ).status_code,
            400,
        )

        # Tarefa pessoal.
        r = self.tarefa(self.cd, projeto=None)
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(
            self.ca.get(f"/api/tarefas/{r.data['id']}/").status_code,
            404,
        )

    def test_checklist_comentarios_materiais(self):
        tid = self.tarefa(self.ca).data['id']

        # Checklist.
        r = self.cb.post(
            '/api/checklist/',
            {'tarefa': tid, 'texto': 'item 1'},
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)
        iid = r.data['id']

        self.assertEqual(
            self.cc.post(
                '/api/checklist/',
                {'tarefa': tid, 'texto': 'x'},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.cc.patch(
                f'/api/checklist/{iid}/',
                {'concluido': True},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(
            self.cb.patch(
                f'/api/checklist/{iid}/',
                {'concluido': True},
                format='json',
            ).data['concluido'],
            True,
        )

        # A listagem do Kanban traz o progresso do checklist.
        lista_tarefas = self.ca.get(
            f'/api/tarefas/?projeto={self.pid}'
        )
        self.assertEqual(
            lista_tarefas.status_code,
            200,
            lista_tarefas.data,
        )
        resultados = lista_tarefas.data.get(
            'results',
            lista_tarefas.data,
        )
        tarefa_listada = next(
            item for item in resultados
            if item['id'] == tid
        )
        self.assertEqual(tarefa_listada['checklist_total'], 1)
        self.assertEqual(tarefa_listada['checklist_concluidos'], 1)
        self.assertEqual(
            self.cd.get(f'/api/checklist/?tarefa={tid}').data,
            [],
        )

        # O autor do comentário vem da autenticação, não do corpo da requisição.
        r = self.cc.post(
            '/api/comentarios/',
            {
                'tarefa': tid,
                'descricao': 'oi',
                'user': self.a.id,
            },
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data['user'], self.c.id)
        self.assertEqual(r.data['autor']['email'], 'c@x.com')
        cid = r.data['id']

        self.assertEqual(
            self.cd.post(
                '/api/comentarios/',
                {'tarefa': tid, 'descricao': 'invasor'},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.ca.patch(
                f'/api/comentarios/{cid}/',
                {'descricao': 'edit'},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(
            self.cc.patch(
                f'/api/comentarios/{cid}/',
                {'descricao': 'edit'},
                format='json',
            ).status_code,
            200,
        )

        # Materiais.
        r = self.cb.post(
            '/api/materiais/',
            {
                'tarefa': tid,
                'titulo': 'Doc',
                'url': 'https://docs.google.com/x',
            },
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)

        r2 = self.ca.post(
            '/api/materiais/',
            {
                'projeto': self.pid,
                'titulo': 'Pasta',
                'url': 'https://drive.google.com/y',
            },
            format='json',
        )
        self.assertEqual(r2.status_code, 201, r2.data)

        self.assertEqual(
            self.ca.post(
                '/api/materiais/',
                {
                    'projeto': self.pid,
                    'tarefa': tid,
                    'titulo': 'z',
                    'url': 'https://a.com',
                },
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.ca.post(
                '/api/materiais/',
                {'titulo': 'z', 'url': 'https://a.com'},
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.ca.post(
                '/api/materiais/',
                {
                    'projeto': self.pid,
                    'titulo': 'z',
                    'url': 'nao-e-url',
                },
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            self.cc.post(
                '/api/materiais/',
                {
                    'projeto': self.pid,
                    'titulo': 'z',
                    'url': 'https://a.com',
                },
                format='json',
            ).status_code,
            400,
        )
        self.assertEqual(
            len(
                self.cc.get(
                    f'/api/materiais/?projeto={self.pid}'
                ).data
            ),
            1,
        )
        self.assertEqual(
            self.cd.get('/api/materiais/').data,
            [],
        )

        # O detalhe traz checklist, comentários e materiais.
        detalhe = self.cc.get(f'/api/tarefas/{tid}/').data
        self.assertEqual(
            (
                len(detalhe['checklist']),
                len(detalhe['comentarios']),
                len(detalhe['materiais']),
            ),
            (1, 1, 1),
        )
        self.assertEqual(
            detalhe['comentarios'][0]['autor']['email'],
            'c@x.com',
        )

    def test_projeto_com_tarefas_aninhadas(self):
        base = {
            'titulo': 'N',
            'prioridade': 1,
            'prazoInicio': '2026-10-24',
            'prazoFim': '2026-10-25',
        }

        r = self.ca.post(
            '/api/projetos/',
            {
                'nome': 'P2',
                'tarefas': [dict(base, user=self.a.id)],
            },
            format='json',
        )
        self.assertEqual(r.status_code, 201, r.data)

        r = self.ca.post(
            '/api/projetos/',
            {
                'nome': 'P3',
                'tarefas': [dict(base, user=self.d.id)],
            },
            format='json',
        )
        self.assertEqual(r.status_code, 400, r.data)

        r = self.ca.patch(
            f'/api/projetos/{self.pid}/',
            {'tarefas': [dict(base, user=self.b.id)]},
            format='json',
        )
        self.assertEqual(r.status_code, 200, r.data)
