from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage


class Command(BaseCommand):
    help = "Envía un correo de prueba usando la configuración SMTP actual."

    def add_arguments(self, parser):
        parser.add_argument("to", type=str, help="Correo destino para la prueba.")

    def handle(self, *args, **options):
        to = options["to"]

        self.stdout.write("SMTP settings detectadas:")
        self.stdout.write(f"- EMAIL_HOST={getattr(settings, 'EMAIL_HOST', None)}")
        self.stdout.write(f"- EMAIL_PORT={getattr(settings, 'EMAIL_PORT', None)}")
        self.stdout.write(f"- EMAIL_USE_TLS={getattr(settings, 'EMAIL_USE_TLS', None)}")
        self.stdout.write(f"- EMAIL_HOST_USER_set={bool(getattr(settings, 'EMAIL_HOST_USER', ''))}")
        self.stdout.write(f"- EMAIL_HOST_PASSWORD_set={bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))}")
        self.stdout.write(f"- DEFAULT_FROM_EMAIL={getattr(settings, 'DEFAULT_FROM_EMAIL', None)}")
        self.stdout.write(f"- EMAIL_TIMEOUT={getattr(settings, 'EMAIL_TIMEOUT', None)}")

        if not getattr(settings, "EMAIL_HOST_USER", "") or not getattr(settings, "EMAIL_HOST_PASSWORD", ""):
            self.stderr.write(
                "Falta configurar EMAIL_HOST_USER/EMAIL_HOST_PASSWORD (revisa tu .env y reinicia runserver)."
            )
            return

        email = EmailMessage(
            subject="INBOTF - Prueba de correo",
            body="Si recibes este mensaje, el SMTP está configurado correctamente.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
            to=[to],
        )

        try:
            sent = email.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f"OK. send() devolvió: {sent}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"FALLÓ el envío: {exc!r}"))
            raise

