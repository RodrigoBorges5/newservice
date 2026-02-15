# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models

# Constantes para status de currículo
CV_STATUS_LABELS = {
    0: "pendente",
    1: "aprovado",
    2: "rejeitado"
}

class Area(models.Model):
    nome = models.CharField(max_length=512, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'area'

class AreaEstudante(models.Model):
    pk = models.CompositePrimaryKey('area', 'estudante_utilizador_auth_user_supabase_field')
    area = models.ForeignKey(Area, models.DO_NOTHING)
    estudante_utilizador_auth_user_supabase_field = models.ForeignKey('Estudante', models.DO_NOTHING, db_column='estudante_utilizador_auth_user_supabase__id')  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'area_estudante'

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)

class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=254)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)

class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class Cr(models.Model):
    tipo = models.SmallIntegerField(blank=True, null=True)
    utilizador_auth_user_supabase_field = models.OneToOneField('Utilizador', models.DO_NOTHING, db_column='utilizador_auth_user_supabase__id', primary_key=True)  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'cr'

class CrCurriculo(models.Model):
    cr_utilizador_auth_user_supabase_field = models.ForeignKey(Cr, models.DO_NOTHING, db_column='cr_utilizador_auth_user_supabase__id')  # Field renamed because it ended with '_'.
    curriculo = models.OneToOneField('Curriculo', models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = 'cr_curriculo'

class Curriculo(models.Model):
    """
    Modelo do currículo do estudante.

    Statuses:
        0 = Pendente (submissão inicial)
        1 = Aprovado
        2 = Rejeitado
    """

    STATUS_PENDENTE = 0
    STATUS_APROVADO = 1
    STATUS_REJEITADO = 2

    file = models.CharField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    validated_date = models.DateField(blank=True, null=True)
    estudante_utilizador_auth_user_supabase_field = models.OneToOneField('Estudante', models.DO_NOTHING, db_column='estudante_utilizador_auth_user_supabase__id')  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'curriculo'

class CVAccessLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    curriculo = models.ForeignKey('Curriculo', on_delete=models.CASCADE)
    accessed_by_user_id = models.UUIDField()  # Alterado de BigIntegerField para UUIDField
    accessed_by_role = models.SmallIntegerField()
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'cv_access_log'

    def approve(self, feedback: str = "") -> None:
        """
        Aprova o currículo e dispara notificação por email ao estudante.

        Args:
            feedback: Comentário opcional do CR.
        """
        from datetime import date
        from .tasks import send_cv_status_notification

        self.status = self.STATUS_APROVADO
        self.validated_date = date.today()
        self.save()

        send_cv_status_notification.enqueue(
            curriculo_id=self.id,
            status=self.STATUS_APROVADO,
            feedback=feedback,
        )

    def reject(self, feedback: str = "") -> None:
        """
        Rejeita o currículo e dispara notificação por email ao estudante.

        Args:
            feedback: Comentário do CR (obrigatório).

        Raises:
            ValueError: Se feedback não for fornecido.
        """
        from datetime import date
        from .tasks import send_cv_status_notification

        if not feedback:
            raise ValueError(
                "Feedback é obrigatório para rejeição de currículo."
            )

        self.status = self.STATUS_REJEITADO
        self.validated_date = date.today()
        self.save()

        send_cv_status_notification.enqueue(
            curriculo_id=self.id,
            status=self.STATUS_REJEITADO,
            feedback=feedback,
        )


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Empresa(models.Model):
    tipo = models.SmallIntegerField(blank=True, null=True, default=1)
    localizacao = models.CharField(max_length=512, blank=True, null=True)
    website = models.CharField(max_length=512, blank=True, null=True)
    utilizador_auth_user_supabase_field = models.OneToOneField('Utilizador', models.DO_NOTHING, db_column='utilizador_auth_user_supabase__id', primary_key=True)  # Field renamed because it ended with '_'.
    # relacao n:n com Area através da tabela EmpresaArea
    areas = models.ManyToManyField(
        'Area',
        through='EmpresaArea',
        through_fields=('empresa_utilizador_auth_user_supabase_field', 'area'),
        related_name='empresas',
    )

    class Meta:
        managed = False
        db_table = 'empresa'


class EmpresaArea(models.Model):
    empresa_utilizador_auth_user_supabase_field = models.ForeignKey(
        Empresa,
        models.DO_NOTHING,
        db_column='empresa_utilizador_auth_user_supabase__id',
    )
    area = models.ForeignKey(Area, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'empresa_area'
        unique_together = (('empresa_utilizador_auth_user_supabase_field', 'area'),)


class Estudante(models.Model):
    tipo = models.SmallIntegerField(blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)
    grau = models.CharField(max_length=512, blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    disponibilidade = models.CharField(max_length=512, blank=True, null=True)
    share_aceites = models.BooleanField(blank=True, null=True)
    utilizador_auth_user_supabase_field = models.OneToOneField('Utilizador', models.DO_NOTHING, db_column='utilizador_auth_user_supabase__id', primary_key=True)  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'estudante'


class Utilizador(models.Model):
    nome = models.CharField(max_length=512, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    tipo = models.SmallIntegerField(blank=True, null=True)
    auth_user_supabase_id = models.UUIDField(db_column='auth_user_supabase__id', primary_key=True)  # Field renamed because it contained more than one '_' in a row.

    class Meta:
        managed = False
        db_table = 'utilizador'


class Vaga(models.Model):
    
    OPORTUNIDADE_CHOICES = [
        ('estagio', 'Estágio'),
        ('emprego', 'Emprego'),
        ('projeto', 'Projeto'),
    ]
    
    nome = models.CharField(unique=True, max_length=512, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    oportunidade = models.CharField(max_length=512, blank=True, null=True, choices=OPORTUNIDADE_CHOICES,)
    visualizacoes = models.IntegerField(blank=True, null=True)
    candidaturas = models.IntegerField(blank=True, null=True)
    empresa_utilizador_auth_user_supabase_field = models.ForeignKey(Empresa, models.DO_NOTHING, db_column='empresa_utilizador_auth_user_supabase__id')  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'vaga'


class VagaArea(models.Model):
    pk = models.CompositePrimaryKey('vaga_id', 'area_id')
    vaga = models.ForeignKey(Vaga, models.CASCADE)
    area = models.ForeignKey(Area, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'vaga_area'


class Notification(models.Model):
    """
    Modelo de notificação para utilizadores.

    Regista notificações enviadas (e.g., alteração de estado do CV)
    e permite rastreio de envio e leitura.

    Tipos de notificação:
        - cv_status_change: Alteração de estado do currículo
        - cv_feedback: Feedback sobre o currículo

    Estados de envio:
        - sent: Enviado com sucesso
        - failed: Falha no envio
    """

    TYPE_CHOICES = [
        ('cv_status_change', 'Alteração de estado do CV'),
        ('cv_feedback', 'Feedback do CV'),
    ]

    STATUS_CHOICES = [
        ('sent', 'Enviado'),
        ('failed', 'Falha'),
    ]

    recipient_user_id = models.UUIDField(
        db_index=True,
        help_text="UUID do utilizador destinatário (Supabase Auth ID)",
    )
    recipient_email = models.EmailField(
        max_length=254,
        help_text="Email do destinatário no momento do envio",
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        db_index=True,
        help_text="Tipo de notificação",
    )
    subject = models.CharField(
        max_length=255,
        help_text="Assunto do email enviado",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        db_index=True,
        help_text="Estado de envio da notificação",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Mensagem de erro em caso de falha",
    )
    read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Se a notificação foi lida pelo utilizador",
    )
    curriculo = models.ForeignKey(
        'Curriculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        db_constraint=False,
        help_text="Currículo associado à notificação (se aplicável)",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification({self.type}, {self.status}) -> {self.recipient_email}"
