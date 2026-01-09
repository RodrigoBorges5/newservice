from rest_framework import serializers
from .models import Curriculo, Estudante


class CurriculoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Curriculo com validação crítica US-2.2.
    
    Valida que o estudante aceitou a partilha de dados (share_aceites = TRUE)
    antes de permitir a submissão do currículo.
    """
    
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
    
    def validate(self, attrs):
        """
        Validação crítica US-2.2: Verificar consentimento de partilha de dados.
        
        Raises:
            serializers.ValidationError: Se o estudante não aceitou a partilha de dados
        """
        # Obter o estudante associado
        estudante = attrs.get('estudante_utilizador_auth_user_supabase_field')
        
               
        if not estudante:
            raise serializers.ValidationError(
                "Estudante não identificado. Por favor, forneça as credenciais corretas."
            )
        
        # Validação crítica: verificar share_aceites
        if not estudante.share_aceites:
            raise serializers.ValidationError({
                'share_aceites': 'Você deve aceitar a partilha de dados antes de submeter o seu currículo. '
                                'Por favor, atualize o seu perfil e aceite os termos de consentimento.'
            })
        
        return attrs
    
    def validate_file(self, value):
        """
        Validação adicional para o campo file (preparação para upload de PDF).
        """
        if value and len(value) > 512:
            raise serializers.ValidationError(
                "O caminho do ficheiro é demasiado longo."
            )
        return value
    
    def create(self, validated_data):
        """
        Criar currículo com status inicial 'Pendente' (0).
        """
        # Definir status inicial como 'Pendente' se não especificado
        if 'status' not in validated_data:
            validated_data['status'] = 0  # Pendente
        
        return super().create(validated_data)
