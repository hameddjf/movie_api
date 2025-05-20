from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Actor(models.Model):
    name = models.CharField(_("نام بازیگر"), max_length=500, unique=True)
    poster = models.URLField(_("تصویر بازیگر"), null=True, blank=True)
    tmdb_id = models.IntegerField(
        _("ایدی بازیگر"), unique=True, null=True, blank=True)
    popularity = models.DecimalField(
        _("معروفیت"), max_digits=5, decimal_places=2, null=True, blank=True)
    movie_count = models.PositiveIntegerField(
        _("تعداد فیلم‌ها"), null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name'], 
                name='unique_actor_name'
            )
        ]

    def get_role(self):
        return 'actor'

    @property
    def average_rating(self):
        return self.imdb_rating

    class Meta:
        verbose_name = _("بازیگر")
        verbose_name_plural = _("بازیگران")

    def __str__(self):
        return self.name


class Director(models.Model):
    tmdb_id = models.IntegerField(_("شناسه TMDB کارگردان"), unique=True,null=True,blank=True)
    full_name = models.CharField(_("نام کارگردان"), max_length=500, unique=True)
    poster = models.URLField(_('تصویر کارگردان'), blank=True, null=True)
    popularity = models.DecimalField(_("معروفیت"), max_digits=5, decimal_places=2, null=True, blank=True)
    movie_count = models.PositiveIntegerField(_("تعداد فیلم‌ها"), null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['full_name'], 
                name='unique_director_name'
            )
        ]

    def get_role(self):
        return 'director'

    @property
    def average_rating(self):
        return self.imdb_rating

    class Meta:
        verbose_name = _("کارگردان")
        verbose_name_plural = _("کارگردان‌ها")

    def __str__(self):
        return self.full_name
