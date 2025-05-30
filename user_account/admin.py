from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from .models import User, WatchlistItem, FavoriteItem, RecentlyWatchedItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'first_name', 'last_name', 'is_staff', 
        'subscription_status', 'has_active_premium_subscription_display', 'date_joined'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'subscription_status', 'preferred_language')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'profile_picture_display', 'profile_picture', 'date_of_birth')}),
        (_('وضعیت اشتراک'), {'fields': ('subscription_status', 'subscription_start_date', 'subscription_end_date')}),
        (_('تنظیمات برگزیده'), {'fields': ('preferred_language', 'preferred_genres')}),
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تاریخ‌های مهم'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined', 'profile_picture_display')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'password2'),
        }),
    )
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="150" height="auto" />', obj.profile_picture.url)
        return _("عکسی آپلود نشده است")
    profile_picture_display.short_description = _("نمایش عکس پروفایل")

    def has_active_premium_subscription_display(self, obj):
        return obj.has_active_premium_subscription()
    has_active_premium_subscription_display.boolean = True
    has_active_premium_subscription_display.short_description = _("اشتراک ویژه فعال")


class UserContentInteractionAdminBase(admin.ModelAdmin):
    list_display = ('user_link', 'content_object_link', 'content_type', 'added_at')
    list_filter = ('user', 'content_type', 'added_at')
    search_fields = ('user__email', 'object_id')
    # readonly_fields = ('user', 'content_type', 'object_id', 'content_object', 'added_at')

    def user_link(self, obj):
        link = reverse("admin:user_account_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', link, obj.user.email)
    user_link.short_description = _("کاربر")
    user_link.admin_order_field = 'user'

    def content_object_link(self, obj):
        if obj.content_object:
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            try:
                link = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{} ({})</a>', link, str(obj.content_object), obj.content_type.name)
            except Exception:
                return f"{str(obj.content_object)} ({obj.content_type.name})"
        return _("محتوا موجود نیست")
    content_object_link.short_description = _("محتوا فیلم")

    # def has_add_permission(self, request):
    #     return False 

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(WatchlistItem)
class WatchlistItemAdmin(UserContentInteractionAdminBase):
    pass


@admin.register(FavoriteItem)
class FavoriteItemAdmin(UserContentInteractionAdminBase):
    pass


@admin.register(RecentlyWatchedItem)
class RecentlyWatchedItemAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'content_object_link', 'watched_at', 'progress_seconds_display')
    list_filter = ('user', 'content_type', 'watched_at')
    search_fields = ('user__email', 'object_id')
    readonly_fields = ('user', 'content_type', 'object_id', 'content_object', 'watched_at', 'progress_seconds')
    ordering = ('-watched_at',)

    def user_link(self, obj):
        link = reverse("admin:accounts_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', link, obj.user.email)
    user_link.short_description = _("کاربر")
    user_link.admin_order_field = 'user'

    def content_object_link(self, obj):
        if obj.content_object:
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            try:
                link = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{} ({})</a>', link, str(obj.content_object), obj.content_type.name)
            except Exception:
                return f"{str(obj.content_object)} ({obj.content_type.name})"
        return _("محتوا موجود نیست")
    content_object_link.short_description = _("محتوا فیلم")

    def progress_seconds_display(self, obj):
        if obj.progress_seconds is not None:
            minutes, seconds = divmod(obj.progress_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"
        return _("N/A")
    progress_seconds_display.short_description = _("پیشرفت تماشا")

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return True