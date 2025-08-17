from django.apps import AppConfig

# Sinyal çalışması ve app bilgileri
class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_app'

    def ready(self):
        import core_app.signals
