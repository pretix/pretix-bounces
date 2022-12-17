from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string
from email.message import Message

from .models import MailAlias


def generate_new_alias(order):
    while True:
        alias = settings.CONFIG_FILE.get('bounces', 'alias') % get_random_string(16)
        with transaction.atomic():
            a, created = MailAlias.objects.get_or_create(sender=alias, defaults={'order': order})
            if created:
                return alias


def generate_new_user_alias(user):
    while True:
        alias = settings.CONFIG_FILE.get('bounces', 'alias') % get_random_string(16)
        with transaction.atomic():
            if MailAlias.objects.filter(sender=alias).exists():
                continue
            a, created = MailAlias.objects.get_or_create(user=user, defaults={'sender': alias})
            return a.sender


def generate_new_customer_alias(customer):
    while True:
        alias = settings.CONFIG_FILE.get('bounces', 'alias') % get_random_string(16)
        with transaction.atomic():
            if MailAlias.objects.filter(sender=alias).exists():
                continue
            a, created = MailAlias.objects.get_or_create(customer=customer, defaults={'sender': alias})
            return a.sender


def get_content(msg: Message):
    if msg.is_multipart():
        plain_body = html_body = None
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                plain_body = plain_body or body.decode(errors='replace')
            elif part.get_content_type() == "text/html":
                body = part.get_payload(decode=True)
                html_body = html_body or body.decode(errors='replace')
        return plain_body or html_body or "Unable to parse email."
    return msg.get_payload(None, True)
