from django.apps import AppConfig

class CrmadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crmAdmin'

    def ready(self):
        import crmAdmin.signals