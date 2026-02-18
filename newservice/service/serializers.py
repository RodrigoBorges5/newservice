from urllib import request
from rest_framework import serializers
from .models import Curriculo,Cr, CrCurriculo, Vaga, Area, VagaArea, CVAccessLog, CV_STATUS_LABELS, Notification

from django.utils import timezone


class CVAccessLogSerializer(serializers.ModelSerializer):
    """Serializer para CVAccessLog - histórico de acessos."""
    accessed_by_user_id = serializers.SerializerMethodField()
    accessed_by_role = serializers.SerializerMethodField()
    
    class Meta:
        model = CVAccessLog
        fields = ['id', 'accessed_by_user_id', 'accessed_by_role', 'accessed_at']
        read_only_fields = fields
    
    def get_accessed_by_user_id(self, obj):
        """Retorna o user_id como string UUID."""
        return str(obj.accessed_by_user_id)
    
    def get_accessed_by_role(self, obj):
        """Retorna o role com label legível."""
        role_labels = {0: 'CR', 1: 'Empresa', 2: 'Estudante'}
        return role_labels.get(obj.accessed_by_role, 'desconhecido')


class CVSignedUrlSerializer(serializers.Serializer):
    """Serializer retornar URL assinada com metadata do CV."""
    id = serializers.IntegerField()
    signed_url = serializers.URLField()
    status = serializers.IntegerField()
    status_label = serializers.SerializerMethodField()
    validated_date = serializers.DateField(allow_null=True)
    expires_in_seconds = serializers.IntegerField(default=900)

    def get_status_label(self, obj):
        """Converte status numérico para label legível."""
        return CV_STATUS_LABELS.get(obj.get('status'), 'desconhecido')


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para listagem de notificações."""

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'subject',
            'status',
            'recipient_email',
            'created_at',
            'updated_at',
            'read',
            'curriculo',
            'error_message',
        ]
        read_only_fields = fields


class NotificationReadSerializer(serializers.ModelSerializer):
    """Serializer para marcar notificação como lida (PATCH)."""

    class Meta:
        model = Notification
        fields = ['id', 'read']
        read_only_fields = ['id']


class AreaSerializer(serializers.Serializer):
    """Serializer para criar/procurar áreas por ID ou nome."""
    id = serializers.IntegerField(required=False, allow_null=True)
    nome = serializers.CharField(required=False, max_length=512, allow_blank=True)

    def validate(self, attrs):
        """Valida que pelo menos um campo (id ou nome) seja fornecido."""
        if not attrs.get('id') and not attrs.get('nome'):
            raise serializers.ValidationError("Deve fornecer 'id' ou 'nome' da área.")
        return attrs


class CurriculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculo
        fields = [
            'id',
            'file',
            'status',
            'descricao',
            'validated_date',
            'estudante_utilizador_auth_user_supabase_field'
            ]
        read_only_fields = ['id', 'status', 'validated_date']
        extra_kwargs = {
            'file': {'required': True, 'allow_blank': False}
        }

    def validate(self, attrs):
        estudante = attrs.get('estudante_utilizador_auth_user_supabase_field')
        if not estudante:
            raise serializers.ValidationError("Estudante não identificado. Por favor, forneça as credenciais corretas.")
        if not estudante.share_aceites:
            raise serializers.ValidationError("Deves aceitar a partilhar os dados a submeter o curriculo. Por favor, aceite os termos de dados.")
        return attrs
    
    def validate_file(self, value):
        if not value.lower().endswith('.pdf'):
            raise serializers.ValidationError("O ficheiro do curriculo deve estar em formato PDF.")
        if len(value) > 255:
            raise serializers.ValidationError("O caminho do ficheiro é demasiado longo.")
        return value
    def create(self, validated_data):
        if 'status' not in validated_data:
            validated_data['status'] = 0  
        return super().create(validated_data)


class VagaSerializer(serializers.ModelSerializer):
    """Serializer para Vaga com suporte a áreas nested."""
    areas = AreaSerializer(many=True, required=False)

    class Meta:
        model = Vaga
        fields = [
            'id',
            'nome',
            'descricao',
            'oportunidade',
            'visualizacoes',
            'candidaturas',
            'empresa_utilizador_auth_user_supabase_field',
            'areas'
        ]
        read_only_fields = ['id', 'visualizacoes', 'candidaturas']
        extra_kwargs = {
            'nome': {'required': True, 'allow_blank': False},
            'descricao': {'required': True, 'allow_blank': False},
            'oportunidade': {'required': True, 'allow_blank': False},
        }

    def validate_oportunidade(self, value):
        """valida que a oportunidade seja uma das opções permitidas."""
        opcoes_validas = ['estagio', 'emprego', 'projeto']
        if value and value not in opcoes_validas:
            raise serializers.ValidationError(
                f"Oportunidade inválida. Opções válidas: {', '.join(opcoes_validas)}"
            )
        return value

    def _obter_ou_criar_area(self, area_data):
        """
        Obtém ou cria uma área baseada em ID ou nome.
        devolve uma instância de Area.
        """
        area_id = area_data.get('id')
        area_nome = area_data.get('nome')

        if area_id:
            # procurar por ID
            try:
                return Area.objects.get(id=area_id)
            except Area.DoesNotExist:
                raise serializers.ValidationError(f"Área com ID {area_id} não encontrada.")
        elif area_nome:
            # procurar ou criar por nome
            area, created = Area.objects.get_or_create(nome=area_nome)
            return area
        else:
            raise serializers.ValidationError("Deve fornecer 'id' ou 'nome' da área.")

    def create(self, validated_data):
        """Cria uma vaga e suas áreas relacionadas."""
        areas_data = validated_data.pop('areas', [])
        
        # criar aa vaga
        vaga = Vaga.objects.create(**validated_data)
        
        # procurar áreas
        for area_data in areas_data:
            area = self._obter_ou_criar_area(area_data)
            # Criar relação na tabela VagaArea
            VagaArea.objects.create(vaga=vaga, area=area)
        
        return vaga

    def update(self, instance, validated_data):
        """Atualiza uma vaga e suas áreas relacionadas."""
        areas_data = validated_data.pop('areas', None)
        
        # Atualizar fields da vaga
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Atualizar áreas se fornecidas
        if areas_data is not None:
            # Remover áreas antigas
            VagaArea.objects.filter(vaga=instance).delete()
            
            # Adicionar novas áreas
            for area_data in areas_data:
                area = self._obter_ou_criar_area(area_data)
                VagaArea.objects.create(vaga=instance, area=area)
        
        return instance

    def to_representation(self, instance):
        """formata a representação para incluir áreas completas."""
        representation = super().to_representation(instance)
        
        # procurar áreas relacionadas
        vaga_areas = VagaArea.objects.filter(vaga=instance).select_related('area')
        representation['areas'] = [
            {'id': va.area.id, 'nome': va.area.nome, 'descricao': va.area.descricao}
            for va in vaga_areas
        ]
        
        return representation

class CRReviewSerializer(serializers.Serializer):
    curriculo_id = serializers.IntegerField(read_only = False)
    status = serializers.ChoiceField(choices=((Curriculo.CV_STATUS_APPROVED, "Aprovado"),(Curriculo.CV_STATUS_REJECTED, "Rejeitado")),error_messages={
            "invalid_choice": "Estado inválido. Valores permitidos: 1 (aprovado) ou 2 (rejeitado).",
            "required": "O campo status é obrigatório."
        })
    feedback = serializers.CharField(allow_blank=True,allow_null=True,required=False)
    review_date = serializers.DateField(read_only=True)

    def validate_curriculo_id(self, value):
        try:
            curriculo = Curriculo.objects.get(id=value)
        except Curriculo.DoesNotExist:
            raise serializers.ValidationError("Currículo não encontrado.")

        if not curriculo.is_pending():
            raise serializers.ValidationError(
                "Este currículo já foi validado."
            )

        return value

    def validate(self, attrs):
        status = attrs.get("status")
        feedback = attrs.get("feedback")

        # Se rejeitado, é obrigatório dar feedback
        if status == Curriculo.CV_STATUS_REJECTED and not feedback:
            raise serializers.ValidationError({
                "feedback": "Feedback é obrigatório quando o currículo é rejeitado."
            })
        return attrs


    def create(self, validated_data):
        request = self.context["request"]

        curriculo = Curriculo.objects.get(id=validated_data["curriculo_id"])

        try:       
            cr = Cr.objects.get(utilizador_auth_user_supabase_field=request.user_id)
        except Cr.DoesNotExist:
            raise serializers.ValidationError(
                "Utilizador autenticado não é um CR válido."
            )

        status = validated_data["status"]
        feedback = validated_data.get("feedback")

        if status == Curriculo.CV_STATUS_APPROVED:
            curriculo.approve()
        elif status == Curriculo.CV_STATUS_REJECTED:
            curriculo.reject()

        # Criação da review
        review = CrCurriculo.objects.create(
            cr_utilizador_auth_user_supabase_field=cr,
            curriculo=curriculo,
            feedback=feedback,
            review_date=curriculo.validated_date,
        )
        return review

class CRReviewResponseSerializer(serializers.Serializer):
    curriculo_id = serializers.IntegerField(source="curriculo.id")
    status = serializers.SerializerMethodField()
    feedback = serializers.CharField(allow_blank=True, allow_null=True)
    review_date = serializers.DateField()
    validated_by = serializers.CharField(
        source="cr_utilizador_auth_user_supabase_field.utilizador_auth_user_supabase_field.nome"
    )

    def get_status(self, obj):
        return obj.curriculo.get_status_display()
