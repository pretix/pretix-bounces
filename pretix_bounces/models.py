from django.db import models


class MailAlias(models.Model):
    sender = models.EmailField(unique=True)
    order = models.ForeignKey('pretixbase.Order', on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
