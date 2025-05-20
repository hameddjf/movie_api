
from django.db import models
from django.utils.translation import gettext_lazy as _

from polymorphic.managers import PolymorphicManager

class ReviewManager(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(approved=True)

class MovieManager(PolymorphicManager):
    def get_by_genre(self, genre_name):
        """
        فیلم‌ها و سریال‌ها را بر اساس نام ژانر برمی‌گرداند.
        جستجو بدون حساسیت به بزرگی و کوچکی حروف انجام می‌شود.
        """
        return self.get_queryset().filter(genres__name__iexact=genre_name)

    def get_published(self):
        """
        فقط آیتم‌هایی که وضعیت انتشار آن‌ها True است را برمی‌گرداند.
        """
        return self.get_queryset().filter(status=True)

    def get_movies_only(self):
        """
        فقط آیتم‌هایی که از نوع 'MOVIE' هستند را برمی‌گرداند.
        """
        from .models import Type 
        return self.get_queryset().filter(type=Type.MOVIE)

    def get_series_only(self):
        """
        فقط آیتم‌هایی که از نوع 'SERIES' هستند را برمی‌گرداند.
        """
        from .models import Type 
        return self.get_queryset().filter(type=Type.SERIES)