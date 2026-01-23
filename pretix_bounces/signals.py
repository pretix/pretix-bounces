import email
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_scopes import scopes_disabled
from email.utils import getaddresses
from imaplib import IMAP4_SSL
from pretix.base.logentrytype_registry import LogEntryType, log_entry_types
from pretix.base.logentrytypes import OrderLogEntryType
from pretix.base.models import OutgoingMail
from pretix.base.signals import global_email_filter, periodic_task

from .models import MailAlias
from .utils import generate_new_alias, get_content


@receiver(global_email_filter, dispatch_uid="pretix_bounces_email_filter_global")
def add_bounce_sender_global(
    sender, message: EmailMultiAlternatives, outgoing_mail, **kwargs
):
    if not settings.CONFIG_FILE.has_section("bounces"):
        return message

    from_domain = settings.CONFIG_FILE.get("bounces", "from_domain", fallback="")
    if from_domain and "@" + from_domain not in message.from_email:
        return message

    alias = generate_new_alias(outgoing_mail)
    from_email = message.from_email

    if "Reply-To" not in message.extra_headers:
        message.extra_headers["Reply-To"] = from_email

    message.from_email = alias
    message.extra_headers.update(
        {
            "From": from_email,
        }
    )
    return message


@receiver(periodic_task, dispatch_uid="pretix_bounces_periodic")
@scopes_disabled()
def get_bounces_via_imap(sender, **kwargs):
    if not settings.CONFIG_FILE.has_section("bounces"):
        return
    host = settings.CONFIG_FILE.get("bounces", "server", fallback="localhost").split(
        ":"
    )[0]
    try:
        port = settings.CONFIG_FILE.get(
            "bounces", "server", fallback="localhost"
        ).split(":")[1]
    except IndexError:
        port = 143
    imap = IMAP4_SSL(host, port)
    imap.login(
        settings.CONFIG_FILE.get("bounces", "user", fallback="pretix"),
        settings.CONFIG_FILE.get("bounces", "pass", fallback=""),
    )
    imap.select()
    typ, data = imap.search(None, "UnSeen")
    for num in data[0].split():
        typ, data = imap.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        imap.store(num, "+FLAGS", "\\Seen")
        to = getaddresses(msg.get_all("To"))
        for name, addr in to:
            try:
                alias = MailAlias.objects.get(sender=addr)
            except MailAlias.DoesNotExist:
                continue
            content = get_content(msg)
            if isinstance(content, bytes):
                content = content.decode(errors="replace")
            full_mail = data[0][1].decode()

            if alias.outgoing_mail:
                alias.outgoing_mail.status = OutgoingMail.STATUS_BOUNCED
                alias.outgoing_mail.error = "Bounce received"
                alias.outgoing_mail.error_detail = full_mail
                alias.outgoing_mail.save(update_fields=["status", "error", "error_detail", "sent"])

            if user := (alias.outgoing_mail.user if alias.outgoing_mail else alias.user):
                user.log_action(
                    "pretix_bounces.user.email.received",
                    data={
                        "subject": msg["Subject"],
                        "message": content,
                        "sender": msg["Sender"],
                        "full_mail": full_mail,
                    },
                )
            if customer := (alias.outgoing_mail.customer if alias.outgoing_mail else alias.customer):
                customer.log_action(
                    "pretix_bounces.order.email.received",
                    data={
                        "subject": msg["Subject"],
                        "message": content,
                        "sender": msg["Sender"],
                        "full_mail": full_mail,
                    },
                )
            if order := (alias.outgoing_mail.order if alias.outgoing_mail else alias.order):
                order.log_action(
                    "pretix_bounces.order.email.received",
                    data={
                        "subject": msg["Subject"],
                        "message": content,
                        "sender": msg["Sender"],
                        "full_mail": full_mail,
                    },
                )
    imap.close()
    imap.logout()


@log_entry_types.new_from_dict({
    "pretix_bounces.order.email.received": _(
        "An email reply has been received by the user."
    ),
})
class OrderBounceLogEntryType(OrderLogEntryType):
    pass


@log_entry_types.new_from_dict({
    "pretix_bounces.user.email.received": _(
        "An email reply has been received by the user."
    ),
})
class UserBounceLogEntryType(LogEntryType):
    pass


@receiver(periodic_task, dispatch_uid="pretix_bounces_periodic_cleanup")
def cleanup_aliases(sender, **kwargs):
    MailAlias.objects.filter(
        datetime__lt=now() - timedelta(days=90), user__isnull=True
    ).delete()
