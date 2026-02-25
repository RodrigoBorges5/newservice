import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Variáveis SMTP obrigatórias em produção (EMAIL_BACKEND = smtp)
_REQUIRED_SMTP_VARS = (
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
)


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "service"

    def ready(self):
        self._validate_email_settings()

    # ── validação de configuração SMTP ───────────────────────────────
    @staticmethod
    def _validate_email_settings():
        from django.conf import settings

        backend = getattr(settings, "EMAIL_BACKEND", "")

        # Só valida se o backend for SMTP (produção)
        if "smtp" not in backend.lower():
            logger.info(
                "[Email] Backend de email: %s — validação SMTP ignorada.",
                backend,
            )
            return

        missing = [
            var for var in _REQUIRED_SMTP_VARS if not getattr(settings, var, None)
        ]

        if missing:
            if settings.DEBUG:
                logger.warning(
                    "[Email] DEBUG=True — variáveis SMTP em falta (%s). "
                    "Emails podem falhar; configure-as ou use o backend de consola.",
                    ", ".join(missing),
                )
            else:
                raise RuntimeError(
                    f"Configuração SMTP incompleta. "
                    f"Variáveis em falta: {', '.join(missing)}. "
                    f"Defina-as no ambiente ou use o backend de consola em desenvolvimento."
                )

        # Log de confirmação SEM expor credenciais (C7)
        logger.info(
            "[Email] SMTP configurado — host=%s, port=%s, tls=%s, ssl=%s, from=%s",
            getattr(settings, "EMAIL_HOST", ""),
            getattr(settings, "EMAIL_PORT", ""),
            getattr(settings, "EMAIL_USE_TLS", ""),
            getattr(settings, "EMAIL_USE_SSL", ""),
            getattr(settings, "DEFAULT_FROM_EMAIL", ""),
        )
