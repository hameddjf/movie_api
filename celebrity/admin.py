from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from .models import Actor, Director
# Register your models here.

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'tmdb_id', 'popularity', 'movie_count')
    search_fields = ('name', 'tmdb_id')
    list_filter = ('popularity',)
    ordering = ('-popularity',) 
    readonly_fields = ('display_poster_in_form',) 
    
    def display_poster(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" width="80" height="125" />', obj.poster
            )
        return _("بدون تصویر")
    display_poster.short_description = _('پوستر')

    def display_poster_in_form(self, obj): 
        if obj.poster:
            return format_html('<img src="{}" width="100" height="150" style="margin-bottom:10px;" />', obj.poster)
        return _("بدون تصویر")
    display_poster_in_form.short_description = _('تصویر پوستر')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
      
class MovieForDirectorInline(admin.TabularInline):
    model = Director.movies_director.through
    extra = 0
    verbose_name = _('فیلم')
    verbose_name_plural = _('فیلم‌های کارگردانی شده')
    fields = ('movie_link',)
    readonly_fields = ('movie_link',)
    
    def movie_link(self, instance):
        if hasattr(instance, 'movie'):
            movie_obj = instance.movie
            from django.urls import reverse
            link = reverse("admin:%s_%s_change" % (movie_obj._meta.app_label, movie_obj._meta.model_name), args=[movie_obj.pk])
            return format_html('<a href="{}">{}</a>', link, movie_obj.title)
        return "-"
    movie_link.short_description = _('عنوان فیلم')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
      
@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    related_movie_field_name = 'movies_director'
    list_display = ('full_name', 'display_poster', 'tmdb_id', 'popularity', 'movie_count')
    search_fields = ('full_name', 'tmdb_id')
    list_filter = ('popularity',)
    ordering = ('-popularity',)
    readonly_fields = ('display_poster_in_form', 'movies_directed_list')
    inlines = [MovieForDirectorInline]
    
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('movies_director')

    def display_poster(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" width="80" height="125" />', obj.poster
            )
        return _("بدون تصویر")
    display_poster.short_description = _('پوستر')

    def movies_for_director(self, obj):
        return ', '.join([movie.title for movie in obj.movies_director.all()])
    movies_for_director.short_description = _('فیلم‌های کارگردان')
    

    def display_poster_in_form(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="100" height="150" style="margin-bottom:10px;" />', obj.poster)
        return _("بدون تصویر")
    display_poster_in_form.short_description = _('تصویر پوستر')

    def get_queryset(self, request):
        qs = super().get_queryset(request) 
        return qs.prefetch_related(self.related_movie_field_name)

    def movies_directed_list(self, obj):
        movies = obj.movies_director.all() 
        if not movies:
            return _("هنوز فیلمی کارگردانی نکرده است.")
        
        movie_links = []
        for movie in movies:
            link = reverse("admin:%s_%s_change" % (movie._meta.app_label, movie._meta.model_name), args=[movie.pk])
            movie_links.append(format_html('<li><a href="{}">{}</a></li>', link, movie.title)) 
        return format_html("<ul>{}</ul>", "".join(movie_links))
    movies_directed_list.short_description = _('فیلم‌های کارگردانی شده')