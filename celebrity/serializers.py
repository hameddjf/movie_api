from rest_framework import serializers

from movielenz.models import Actor, Director

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = [
            'id',
            'name',
            'poster',
            'tmdb_id',
            'popularity',
            'movie_count', 
            'average_rating', 
            'get_role',
        ]
        read_only_fields = ['id', 'get_role', 'average_rating']
        

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = [
            'id',
            'full_name',
            'poster',
            'tmdb_id',
            'popularity',
            'movie_count',
            'average_rating',
            'get_role',
        ]
        read_only_fields = ['id', 'get_role', 'average_rating']