from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from movielenz.models import Movie, Series
# Create your models here.

class Episode(models.Model):
    movie = models.ForeignKey(
        Movie,
        related_name='episodes',
        on_delete=models.CASCADE,
        verbose_name=_("فیلم و سریال")
    )
    season = models.PositiveIntegerField(_("فصل"), default=1, blank=True, null=True)
    title = models.CharField(_("عنوان قسمت"), max_length=500)
    slug = models.SlugField(_("Slug"), max_length=500, unique=True, blank=True)
    created_at = models.DateTimeField(_("ایجاد شده"), auto_now_add=True)
    updated_at = models.DateTimeField(_("به‌روزرسانی شده"), auto_now=True)

    class Meta:
        verbose_name = _("قسمت")
        verbose_name_plural = _("قسمت‌ها")

    def __str__(self):
        if isinstance(self.movie, Series): 
            return f"فصل {self.season} - {self.title}"
        else:
            return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not isinstance(self.movie, Series): 
            self.season = None 
        super(Episode, self).save(*args, **kwargs)
        
class EpisodeQuality(models.Model):
    QUALITY_CHOICES = [
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('4k', '4K'),
    ]
    
    episode = models.ForeignKey(
        Episode,
        related_name='qualities',
        on_delete=models.CASCADE,
        verbose_name=_("قسمت")
    )
    quality = models.CharField(_("کیفیت"), max_length=50, choices=QUALITY_CHOICES)
    file = models.FileField(_("فایل ویدیو"), upload_to='episodes/', max_length=255)

    class Meta:
        verbose_name = _("کیفیت قسمت")
        verbose_name_plural = _("کیفیت‌های قسمت")

    def __str__(self):
        return f"{self.episode.title} - {self.quality}"