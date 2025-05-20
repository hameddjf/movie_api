from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from movielenz.models import Movie

from .models import Episode, EpisodeQuality


class BasicEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('id', 'title', 'slug', 'created_at', 'updated_at') 
        read_only_fields = fields

class MovieSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie 
        fields = ('id', 'title', "type") 
class EpisodeQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeQuality
        fields = ('id', 'quality', 'file', 'episode')
        read_only_fields = ('id',)

class EpisodeQualityDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش جزئیات کیفیت، بدون نمایش مجدد اطلاعات قسمت"""
    class Meta:
        model = EpisodeQuality
        fields = ('id', 'quality', 'file')
        read_only_fields = ('id',)
        
        
class EpisodeGroupItemSerializer(serializers.ModelSerializer):
    qualities = EpisodeQualityDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = (
            'id',
            'title',
            'slug',
            'qualities',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class EpisodeSerializer(serializers.ModelSerializer):
    qualities = EpisodeQualityDetailSerializer(many=True, read_only=True) 
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True,
        label=_("فیلم/سریال")
    )

    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Episode
        fields = (
            'id',
            'movie_id', 
            'movie_title', 
            'season',
            'title',
            'slug',
            'qualities',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def validate(self, data):
        movie = data.get('movie') 
        season = data.get('season')
        return data

    def create(self, validated_data):
        episode = Episode.objects.create(**validated_data)
        return episode

    def update(self, instance, validated_data):
        instance.movie = validated_data.get('movie', instance.movie)
        instance.title = validated_data.get('title', instance.title)
        instance.season = validated_data.get('season', instance.season)

        instance.save() 
        return instance
    
