from django.conf import settings

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = 'pretix_bounces'
    verbose_name = 'Bounce processing for pretix'

    class PretixPluginMeta:
        name = 'Bounce processing for pretix'
        author = 'Raphael Michel'
        description = 'Allows automatic processing of bounces or automatic replies to emails sent by pretix.'
        visible = False
        version = __version__
        compatibility = "pretix>=3.1.0"

    def ready(self):
        settings.CORE_MODULES.add('pretix_bounces')
        from . import signals  # NOQA


