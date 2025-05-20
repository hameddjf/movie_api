from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Episode, EpisodeQuality
# Register your models here.

class EpisodeQualityInline(admin.TabularInline):
    model = EpisodeQuality
    extra = 1 
    fields = ('quality', 'file')
    verbose_name = _("کیفیت")
    verbose_name_plural = _("کیفیت‌ها")

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'movie_title', 'season_display', 'created_at', 'updated_at')
    list_filter = ('movie__title', 'season', 'created_at')
    search_fields = ('title', 'movie__title') 
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EpisodeQualityInline]
    ordering = ('movie__title', 'season', 'title') 

    fieldsets = (
        (None, {
            'fields': ('movie', 'title', 'slug')
        }),
        (_("اطلاعات فصل (اختیاری برای سریال‌ها)"), {
            'fields': ('season',),
            'classes': ('collapse',), # به صورت پیش‌فرض بسته باشد
            'description': _("این بخش تنها برای قسمت‌های سریال کاربرد دارد.")
        }),
        (_("تاریخ‌ها"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def movie_title(self, obj):
        return obj.movie.title
    movie_title.short_description = _("فیلم/سریال")
    movie_title.admin_order_field = 'movie__title'

    def season_display(self, obj):
        if obj.season is not None: 
            return obj.season
        return _("تک قسمتی")
    season_display.short_description = _("فصل")
    season_display.admin_order_field = 'season'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(EpisodeQuality)
class EpisodeQualityAdmin(admin.ModelAdmin):
    list_display = ('episode_title', 'quality', 'file_info')
    list_filter = ('quality', 'episode__movie__title', 'episode__season')
    search_fields = ('episode__title', 'episode__movie__title')
    autocomplete_fields = ['episode']
    ordering = ('episode__movie__title', 'episode__season', 'episode__title', 'quality')

    def episode_title(self, obj):
        return obj.episode.title
    episode_title.short_description = _("عنوان قسمت")
    episode_title.admin_order_field = 'episode__title'

    def file_info(self, obj):
        if obj.file:
            return obj.file.name
        return _("فایل موجود نیست")
    file_info.short_description = _("فایل")
