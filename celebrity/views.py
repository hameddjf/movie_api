from django_filters.rest_framework import DjangoFilterBackend 

from rest_framework import generics, filters

from .models import Actor, Director
from .serializers import ActorSerializer, DirectorSerializer

# --- Actore views ---

class ActorListAPIView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of actors.
    Supports filtering, searching, and ordering.
    """
    queryset = Actor.objects.all().order_by('-popularity')
    serializer_class = ActorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'popularity': ['exact', 'gte', 'lte', 'gt', 'lt'],
        'movie_count': ['exact', 'gte', 'lte', 'gt', 'lt'],
    }
    search_fields = ['name', 'tmdb_id'] 
    ordering_fields = ['name', 'popularity', 'movie_count'] 

class ActorDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific actor.
    """
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


# --- Director Views ---

class DirectorListAPIView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of directors.
    Supports filtering, searching, and ordering.
    """
    queryset = Director.objects.all().order_by('-popularity')
    serializer_class = DirectorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'popularity': ['exact', 'gte', 'lte', 'gt', 'lt'],
        'movie_count': ['exact', 'gte', 'lte', 'gt', 'lt'],
    }
    search_fields = ['full_name', 'tmdb_id']
    ordering_fields = ['full_name', 'popularity', 'movie_count']

class DirectorDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific director.
    """
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer

# class ActorViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows actors to be viewed or edited.
#     """
#     queryset = Actor.objects.all().order_by('-popularity')
#     serializer_class = ActorSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['popularity'] # مثال: /api/actors/?popularity=8.5
#     search_fields = ['name', 'tmdb_id'] # مثال: /api/actors/?search=Tom Hanks
#     ordering_fields = ['name', 'popularity', 'movie_count']
    

# class DirectorViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows directors to be viewed or edited.
#     """
#     queryset = Director.objects.all().order_by('-popularity')
#     serializer_class = DirectorSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['popularity']
#     search_fields = ['full_name', 'tmdb_id']
#     ordering_fields = ['full_name', 'popularity', 'movie_count']