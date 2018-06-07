from django.apps import AppConfig
from django.conf import settings


class PluginApp(AppConfig):
    name = 'pretix_bounces'
    verbose_name = 'Bounce processing for pretix'

    class PretixPluginMeta:
        name = 'Bounce processing for pretix'
        author = 'Raphael Michel'
        description = 'Allows automatic processing of bounces or automatic replies to emails sent by pretix.'
        visible = False
        version = '1.0.1'

    def ready(self):
        settings.CORE_MODULES.add('pretix_bounces')
        from . import signals  # NOQA


default_app_config = 'pretix_bounces.PluginApp'
