from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    اجازه دسترسی کامل به ادمین‌ها، و دسترسی فقط خواندنی به دیگران.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: 
            return True
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    اجازه ویرایش فقط به صاحب آبجکت. دیگران فقط دسترسی خواندنی دارند.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user 