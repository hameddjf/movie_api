# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserRegistrationView, UserProfileView,
    WatchlistViewSet, FavoriteViewSet, RecentlyWatchedViewSet
)


router = DefaultRouter()
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'history', RecentlyWatchedViewSet, basename='recentlywatched')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),

]
