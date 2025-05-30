from django.db import models
from django.utils.translation import gettext_lazy as _

class SubscriptionStatus(models.TextChoices):
    FREE = 'free', _('رایگان')
    PREMIUM = 'premium', _('ویژه')
    CANCELLED = 'cancelled', _('لغو شده')
    EXPIRED = 'expired', _('منقضی شده')