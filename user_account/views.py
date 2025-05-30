import logging
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.urls import resolve, Resolver404

from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import WatchlistItem, FavoriteItem, RecentlyWatchedItem
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    WatchlistItemSerializer, FavoriteItemSerializer, RecentlyWatchedItemSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    http_method_names = ['get', 'patch', 'head', 'options']
    

    def get_object(self):
        return self.request.user 

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class BaseUserContentInteractionViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.Meta.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        content_type = serializer.context.get('content_type_model')
        object_id = request.data.get('object_id')
        
        current_status = status.HTTP_201_CREATED
        if hasattr(serializer, '_is_existing_instance') and serializer._is_existing_instance:
            current_status = status.HTTP_200_OK
            
        return Response(serializer.data, status=current_status, headers=headers)
        
        # if self.Meta.model in [WatchlistItem, FavoriteItem]:
        #     if self.Meta.model.objects.filter(
        #         user=request.user, 
        #         content_type=content_type, 
        #         object_id=object_id
        #     ).exists():
        #         return Response(
        #             {"detail": _("این آیتم از قبل در لیست شما وجود دارد.")},
        #             status=status.HTTP_400_BAD_REQUEST
        #         )
        
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['delete'], url_path='content')
    def delete_by_content_item(self, request, *args, **kwargs):
        content_item_url = request.data.get('content_item_url')

        if not content_item_url:
            return Response(
                {"content_item_url": [_("This field is required.")]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parsed_url = urlparse(content_item_url)
            path = parsed_url.path
            match = resolve(path)
        except Resolver404:
            return Response({'content_item_url': _("URL path does not match any known patterns.")}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'content_item_url': _("Invalid URL format or path: %(error)s") % {'error': str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        serializer_class = self.get_serializer_class()
        temp_serializer_instance = serializer_class() 
        
        model_class = temp_serializer_instance._get_model_from_view_match(match)

        if not model_class:
            return Response({'content_item_url': _("Could not determine the model type from the provided URL.")}, status=status.HTTP_400_BAD_REQUEST)

        object_pk_str = match.kwargs.get('pk')
        if not object_pk_str:
            for kw_val in match.kwargs.values():
                if isinstance(kw_val, (int, str)) and str(kw_val).isdigit():
                    object_pk_str = str(kw_val)
                    break
            if not object_pk_str:
                return Response({'content_item_url': _("Could not extract object ID from the URL.")}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            object_pk = int(object_pk_str)
        except ValueError:
            return Response({'content_item_url': _("Object ID extracted from URL is not a valid integer.")}, status=status.HTTP_400_BAD_REQUEST)
        content_type_resolved = ContentType.objects.get_for_model(model_class)
        try:
            instance = self.Meta.model.objects.filter(
                user=request.user,
                content_type=content_type_resolved,
                object_id=object_pk
            ).first()

            if instance:
                self.perform_destroy(instance) 
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": _("آیتم یافت نشد.")}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e: 
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting interaction item for user {request.user.id} with content_type {content_type_resolved.id}, object_id {object_pk}: {e}")
            return Response({"detail": _("An error occurred while deleting the item.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WatchlistViewSet(BaseUserContentInteractionViewSet):
    serializer_class = WatchlistItemSerializer
    
    class Meta:
        model = WatchlistItem

class FavoriteViewSet(BaseUserContentInteractionViewSet):
    serializer_class = FavoriteItemSerializer

    class Meta:
        model = FavoriteItem

class RecentlyWatchedViewSet(BaseUserContentInteractionViewSet):
    serializer_class = RecentlyWatchedItemSerializer

    class Meta:
        model = RecentlyWatchedItem

    def get_queryset(self):
        return super().get_queryset().order_by('-watched_at')