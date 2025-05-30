# accounts/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import resolve, Resolver404, reverse, NoReverseMatch
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from urllib.parse import urlparse

from rest_framework import serializers

from .models import WatchlistItem, FavoriteItem, RecentlyWatchedItem, User

from movielenz.models import Genre

class BaseContentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)

    class Meta:
        fields = ['id', 'title'] #, 'type']


User = get_user_model()

class ContentObjectRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `content_object` generic relationship.
    """
    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        return {
            'id': value.pk,
            'title': str(value),
            'type': value.__class__.__name__.lower()
        }

    def to_internal_value(self, data):
        raise NotImplementedError("Direct assignment to content_object is not supported via this field.")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label=_("Confirm password"), style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'date_of_birth')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    preferred_genre_ids = serializers.PrimaryKeyRelatedField(
        # queryset=ContentType.objects.none(),
        queryset = Genre.objects.none(),
        many=True, source='preferred_genres', 
        write_only=True, 
        help_text=_("لیستی از ID های ژانرهای مورد علاقه"),
        required=False
    )
    preferred_genres_hyperlinks = serializers.HyperlinkedRelatedField(
        many=True,
        source='preferred_genres', 
        read_only=True,          
        view_name='genre-detail',
        help_text=_("لینک به ژانرهای مورد علاقه (فقط خواندنی).")
    )
    preferred_genres_display = serializers.StringRelatedField(
        source='preferred_genres',
        many=True,
        read_only=True,
        help_text=_("نام ژانرهای مورد علاقه (فقط خواندنی).")
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'profile_picture', 
            'date_of_birth', 'subscription_status', 'subscription_end_date',
            'preferred_language', 'preferred_genres_display',
            'preferred_genres_hyperlinks','preferred_genre_ids',
            'last_login', 'date_joined'
        )
        read_only_fields = ('email', 'subscription_status', 'subscription_end_date', 'last_login', 'date_joined', 'id',)
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'profile_picture': {'required': False, 'allow_null': True},
            'date_of_birth': {'required': False, 'allow_null': True},
            'preferred_language': {'required': False},
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            actual_queryset = Genre.objects.all()
            if 'preferred_genre_ids' in self.fields:
                self.fields['preferred_genre_ids'].queryset = actual_queryset
            if 'preferred_genres_hyperlinks' in self.fields:
                self.fields['preferred_genres_hyperlinks'].queryset = actual_queryset
        except ImportError:
            pass


# ----- Serializers for User-Content Interactions -----

class BaseUserContentInteractionSerializer(serializers.ModelSerializer):
    # content_type_name = serializers.CharField(write_only=True, help_text=_("نام مدل محتوا (مثلا: 'movie' یا 'series')"))
    # object_id = serializers.IntegerField(write_only=True, help_text=_("شناسه شیء محتوا"))
    
    content_item_url = serializers.URLField(
        write_only=True, 
        help_text=_('{"content_item_url" : "http://127.0.0.1:8000/movie/3/)"}')
    )
    
    content_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None
        fields = ('id', 'user', 'content_item_url', 'content_details', 'added_at')
        read_only_fields = ('user', 'added_at', 'id')
        
    def _get_model_from_view_match(self, match):
        """
         مدل را از resolved URL match استخراج کند.
        """
        view_class = getattr(match.func, 'cls', None)
        if not view_class:
            return None
        
        queryset = getattr(view_class, 'queryset', None)
        if queryset is not None:
            return queryset.model
        
        serializer_class = getattr(view_class, 'serializer_class', None)
        if serializer_class and hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'model'):
            return serializer_class.Meta.model
            
        return None

    def get_content_details(self, obj):
        if obj.content_object:
            request = self.context.get('request')
            item_url = None
            model_to_view_name_map = self.context.get('model_to_view_name_map', {})
            view_name = model_to_view_name_map.get(obj.content_type.model)

            if request and view_name:
                try:
                    item_url = reverse(view_name, kwargs={'pk': obj.content_object.pk}, request=request)
                except NoReverseMatch:
                    item_url = _("URL not resolvable") # یا None

            return {
                'id': obj.content_object.pk,
                'title': getattr(obj.content_object, 'title', str(obj.content_object)), # فرض بر اینکه 'title' وجود دارد
                'type': obj.content_type.model,
                'url': item_url
            }
        return None

    def validate(self, attrs):
        content_item_url = attrs.get('content_item_url')
        current_user = self.context['request'].user
        if self.instance and not content_item_url:
            return super().validate(attrs)
        if not self.instance and not content_item_url:
            raise serializers.ValidationError({"content_item_url": _("This field is required for creation.")})
        if content_item_url:
            try:
                parsed_url = urlparse(content_item_url)
                path = parsed_url.path
                match = resolve(path)
            except Resolver404:
                raise serializers.ValidationError({'content_item_url': _("URL path does not match any known patterns.")})
            except Exception as e:
                raise serializers.ValidationError({'content_item_url': _("Invalid URL format or path: %(error)s") % {'error': str(e)}})

            model_class = self._get_model_from_view_match(match)
            if not model_class:
                raise serializers.ValidationError({'content_item_url': _("Could not determine the model type from the provided URL.")})

            object_pk_str = match.kwargs.get('pk')
            if not object_pk_str:
                for kw_val in match.kwargs.values():
                    if isinstance(kw_val, (int, str)) and str(kw_val).isdigit():
                        object_pk_str = str(kw_val)
                        break
                if not object_pk_str:
                    raise serializers.ValidationError({'content_item_url': _("Could not extract object ID from the URL.")})
            try:
                object_pk = int(object_pk_str)
            except ValueError:
                 raise serializers.ValidationError({'content_item_url': _("Object ID extracted from URL is not a valid integer.")})
            if not model_class.objects.filter(pk=object_pk).exists():
                raise serializers.ValidationError({'content_item_url': _("The content object linked by the URL does not exist.")})
            
            content_type_resolved = ContentType.objects.get_for_model(model_class)
            
            attrs['resolved_content_type'] = content_type_resolved
            attrs['resolved_object_id'] = object_pk

            if not self.instance:
                InteractionModel = self.Meta.model 
                existing_item = InteractionModel.objects.filter(
                    user=current_user, 
                    content_type=content_type_resolved, 
                    object_id=object_pk
                ).first()
                if existing_item:
                    attrs['existing_item_instance'] = existing_item
                # if InteractionModel.objects.filter(
                #     user=current_user, 
                #     content_type=content_type_resolved, 
                #     object_id=object_pk
                # ).exists():
                #     raise serializers.ValidationError(_("This item is already in your list."))
        return attrs

    def create(self, validated_data):
        existing_item = validated_data.pop('existing_item_instance', None)
        if existing_item:
            self.instance = existing_item
            self._is_existing_instance = True
            return self.instance

        self._is_existing_instance = False
        
        validated_data.pop('content_item_url', None) 
        
        content_type = validated_data.pop('resolved_content_type')
        object_id = validated_data.pop('resolved_object_id')
        
        validated_data['user'] = self.context['request'].user
        validated_data['content_type'] = content_type
        validated_data['object_id'] = object_id
        
        try:
            return super().create(validated_data)
        except IntegrityError:
            InteractionModel = self.Meta.model
            instance = InteractionModel.objects.filter(
                user=validated_data['user'], 
                content_type=validated_data['content_type'], 
                object_id=validated_data['object_id']
            ).first()
            if instance:
                self.instance = instance
                self._is_existing_instance = True
                return instance
            raise serializers.ValidationError(_("This item is already in your list (database constraint)."))
        except Exception as e:
            raise serializers.ValidationError(str(e))


class WatchlistItemSerializer(BaseUserContentInteractionSerializer):
    class Meta(BaseUserContentInteractionSerializer.Meta):
        model = WatchlistItem


class FavoriteItemSerializer(BaseUserContentInteractionSerializer):
    class Meta(BaseUserContentInteractionSerializer.Meta):
        model = FavoriteItem

      
class RecentlyWatchedItemSerializer(BaseUserContentInteractionSerializer):
    progress_seconds = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = RecentlyWatchedItem
        fields = (
            'id',
            'user',
            "content_item_url",
            # 'content_type_name',
            # 'object_id',        
            'content_details',
            'watched_at',     
            'progress_seconds'
        )
        read_only_fields = ('user', 'id', 'watched_at')

    def create(self, validated_data):
        ModelClass = self.Meta.model
        user_instance = validated_data['user']
        content_type = validated_data.pop('resolved_content_type')
        object_id = validated_data.pop('resolved_object_id')
        validated_data.pop('content_item_url', None)

        lookup_data = {
            'user': user_instance,
            'content_type': content_type,
            'object_id': object_id,
        }
        defaults_data = {
            # 'progress_seconds': validated_data.get('progress_seconds', self.fields['progress_seconds'].default),
            'progress_seconds': validated_data.get('progress_seconds'),
            'watched_at': timezone.now()
        }
        instance, created = ModelClass.objects.update_or_create(
            **lookup_data,
            defaults=defaults_data
        )
        return instance

    def update(self, instance, validated_data):
        instance.progress_seconds = validated_data.get('progress_seconds', instance.progress_seconds)
        instance.watched_at = timezone.now()
        instance.save(update_fields=['progress_seconds', 'watched_at'])
        return instance