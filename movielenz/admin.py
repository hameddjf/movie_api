from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from mptt.admin import DraggableMPTTAdmin

from .models import Genre, IpAddress, Movie, Series, Type
# Register your models here.

@admin.register(IpAddress)
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ('ip_address',)
    search_fields = ('ip_address',)
    
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'translated_genre', 'tmdb_id')
    search_fields = ('name', 'translated_genre')
    list_filter = ('name',)

@admin.register(Type)
class TypeAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 20
    list_display = ('tree_actions', 'indented_title', 'slug')
    list_display_links = ('indented_title',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']

# Base Admin for common configurations (optional, but helps reduce redundancy)
class BaseMediaAdminConfig:
    autocomplete_fields = ['actors', 'directors', 'genres']
    search_fields = ('title', 'imdb_id', 'tmdb_id')
    common_fieldsets_1 = (
        (None, {
            'fields': ('title', 'slug', 'status', 'release_date', 'description')
        }),
    )
    common_fieldsets_2 = (
        (_("Additional Information"), {
            'fields': ('actors', 'directors', 'genres', 'duration', 'poster', 'trailer',
                       'production_country', 'language', 'network', 'is_dubbed', 'is_subtitled')
        }),
        (_("IDs and Ratings"), {
            'fields': ('imdb_id', 'tmdb_id', 'imdb_rating', 'tmdb_user_score', 'tmdb_popularity')
        }),
    )

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin, BaseMediaAdminConfig):
    list_display = ('title', 'status', 'release_date', 'imdb_rating')
    list_filter = ('status', 'is_dubbed', 'is_subtitled', 'genres', 'type')
    # readonly_fields = ('type',)

    fieldsets = (
        BaseMediaAdminConfig.common_fieldsets_1 +
        ((_("Type"), {'fields': ('type',)}),) +
        BaseMediaAdminConfig.common_fieldsets_2
    )

    # def type_display_name(self, obj):
    #     return obj.type.name if obj.type else '-'
    # type_display_name.short_description = _('Type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        movie_type_obj = Type.objects.filter(slug='movie').first()
        if movie_type_obj:
            return qs.filter(type=movie_type_obj)
        return qs.exclude(series__isnull=False)

    def save_model(self, request, obj, form, change):
        if not obj.type_id:
            movie_type_obj, created = Type.objects.get_or_create(slug='movie',)
            obj.type = movie_type_obj
        super().save_model(request, obj, form, change)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin, BaseMediaAdminConfig):
    base_model = Series 
    list_display = ('title', 'status', 'release_date', 'imdb_rating', 'number_of_seasons', 'series_status')
    list_filter = ('status', 'series_status', 'is_dubbed', 'is_subtitled', 'genres', 'type')
    # readonly_fields = ('type',)

    fieldsets = (
        BaseMediaAdminConfig.common_fieldsets_1 +
        ((_("Type"), {'fields': ('type',)}),) +
        ((_("Series Details"), {
            'fields': ('number_of_seasons', 'episode_count', 'series_status')
        }),) +
        BaseMediaAdminConfig.common_fieldsets_2
    )
    
    # def type_display_name(self, obj):
    #     return obj.type.name if obj.type else '-'
    # type_display_name.short_description = _('Type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        series_type_obj = Type.objects.filter(slug='series').first()
        if series_type_obj:
            return qs.filter(type=series_type_obj)
        return qs

    def save_model(self, request, obj, form, change):
        series_type_obj, created = Type.objects.get_or_create(slug='series',)
        obj.type = series_type_obj
        super().save_model(request, obj, form, change)