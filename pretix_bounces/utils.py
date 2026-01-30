from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils.crypto import get_random_string
from email.message import Message

from .models import MailAlias


def generate_new_alias(outgoing_mail):
    while True:
        alias = settings.CONFIG_FILE.get("bounces", "alias") % get_random_string(16)
        with transaction.atomic():
            try:
                a, created = MailAlias.objects.get_or_create(
                    outgoing_mail=outgoing_mail,
                    defaults={
                        "sender": alias,
                    }
                )
            except IntegrityError:
                pass
            return a.sender


def get_content(msg: Message):
    if msg.is_multipart():
        plain_body = html_body = None
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                plain_body = plain_body or body.decode(errors="replace")
            elif part.get_content_type() == "text/html":
                body = part.get_payload(decode=True)
                html_body = html_body or body.decode(errors="replace")
        return plain_body or html_body or "Unable to parse email."
    return msg.get_payload(None, True)
