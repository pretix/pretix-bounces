from django.db import models


class MailAlias(models.Model):
    sender = models.EmailField(unique=True)
    order = models.ForeignKey('pretixbase.Order', on_delete=models.CASCADE, null=True)
    user = models.OneToOneField('pretixbase.User', on_delete=models.CASCADE, null=True)
    customer = models.OneToOneField('pretixbase.Customer', on_delete=models.CASCADE, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
