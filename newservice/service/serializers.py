from rest_framework import serializers
from .models import Curriculo


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
