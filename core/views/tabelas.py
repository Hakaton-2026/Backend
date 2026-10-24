class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.prefetch_related("tarefas__itens")
    serializer_class = TemplateSerializer

    @decorators.action(detail=True, methods=["post"])
    def usar(self, request, pk=None):
        projeto = criar_projeto_do_modelo(
            self.get_object(), request.data["nome"], request.user)
        return response.Response(ProjectSerializer(projeto).data, status=201)