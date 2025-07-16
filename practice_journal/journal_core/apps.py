from django.apps import AppConfig


class JournalCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'practice_journal.journal_core'
    label = 'journal_core'

    def ready(self):
        import practice_journal.journal_core.signals