from django.db import transaction

@transaction.atomic
def criar_projeto_do_modelo(template, nome, dono):
    projeto = Project.objects.create(nome=nome, dono=dono)
    for t in template.tarefas.prefetch_related("itens"):
        tarefa = Task.objects.create(projeto=projeto, titulo=t.titulo,
                                     descricao=t.descricao, ordem=t.ordem)
        ChecklistItem.objects.bulk_create(
            ChecklistItem(tarefa=tarefa, texto=i.texto) for i in t.itens.all()
        )
    return projeto