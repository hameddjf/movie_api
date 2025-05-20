# در فایل views.py

from itertools import groupby
from django.db.models import Prefetch, Q

from rest_framework import viewsets, mixins, permissions ,status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from movielenz.models import Type, Movie

from .models import EpisodeQuality # مطمئن شوید Type enum وارد شده است
from .serializers import BasicEpisodeSerializer # سریالایزری که در مرحله ۱ به‌روزرسانی شد

# class CombinedEpisodeQualityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     serializer_class = BasicEpisodeSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

#     filterset_fields = {
#         'episode__movie': ['exact'],
#         'episode__movie__title': ['icontains', 'exact'],
#         'episode__movie__type': ['exact', 'in'],
#         'episode__season': ['exact', 'isnull'], # برای فیلتر کردن بر اساس فصل همچنان مفید است
#         'quality': ['exact', 'in'],
#         'episode__title': ['icontains'],
#     }
    
#     search_fields = [
#         'episode__title', 
#         'episode__movie__title', 
#         'quality',
#         'episode__slug'
#     ]
    
#     ordering_fields = [
#         'episode__movie__title', 
#         'episode__season', 
#         'quality', 
#         'episode__title',
#         'episode__created_at'
#     ]
    
#     # ترتیب‌دهی برای groupby: ابتدا فیلم، سپس فصل (برای سریال‌ها)، سپس کیفیت
#     ordering = ['episode__movie__title', 'episode__movie__id', 'episode__season', 'quality']

#     def get_queryset(self):
#         queryset = EpisodeQuality.objects.select_related(
#             'episode',
#             'episode__movie'
#         ).all()
#         # اگر از polymorphic استفاده می‌کنید، اطمینان حاصل کنید که movie به درستی resolve می‌شود.
#         # queryset = queryset.prefetch_related(
#         # Prefetch('episode__movie', queryset=Movie.objects.select_subclasses())
#         # ) # در صورت نیاز به prefetch صریح زیرکلاس‌ها
#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         result_data = {}

#         # گروه بندی اولیه بر اساس فیلم
#         for movie_instance, eq_for_movie_iter in groupby(queryset, key=lambda eq: eq.episode.movie):
#             movie_title_key = movie_instance.title
#             eq_for_movie_list = list(eq_for_movie_iter) # برای استفاده‌های چندباره

#             # اگر فیلم از نوع سریال است
#             if movie_instance.type == Type.SERIES: # Type.SERIES باید 'SR' یا معادل آن باشد
#                 movie_payload = {} # برای نگهداری فصل‌های این سریال
                
#                 # گروه بندی داخلی بر اساس فصل برای سریال‌ها
#                 # eq_for_movie_list از قبل بر اساس فصل مرتب شده (به لطف ordering اصلی)
#                 for season_number, eq_for_season_iter in groupby(eq_for_movie_list, key=lambda eq: eq.episode.season):
#                     # ایجاد کلید فصل مانند "season-1" یا "season-0" برای قسمت‌های بدون فصل مشخص
#                     season_key = f"season-{season_number}" if season_number is not None else "season-0" # یا هر نام دیگری برای فصل نامشخص
#                     eq_for_season_list = list(eq_for_season_iter)

#                     qualities_data_for_season = [] # لیست کیفیت‌ها برای این فصل
                    
#                     # گروه بندی داخلی‌تر بر اساس کیفیت (برای هر فصل)
#                     # eq_for_season_list از قبل بر اساس کیفیت مرتب شده
#                     for quality_value, eq_for_quality_iter in groupby(eq_for_season_list, key=lambda eq: eq.quality):
#                         unique_episodes = {eq.episode.id: eq.episode for eq in eq_for_quality_iter}
#                         # مرتب‌سازی قسمت‌ها در اینجا اختیاری است، چون از قبل بر اساس عنوان/شناسه مرتب شده‌اند
#                         # sorted_episodes = sorted(list(unique_episodes.values()), key=lambda ep: ep.title)
#                         serialized_episodes = BasicEpisodeSerializer(list(unique_episodes.values()), many=True).data
                        
#                         # ساختار درخواستی برای هر کیفیت
#                         qualities_data_for_season.append({
#                             quality_value: [{"episodes": serialized_episodes}]
#                         })
                    
#                     # ساختار درخواستی برای هر فصل
#                     movie_payload[season_key] = [{"qualities": qualities_data_for_season}]
                
#                 result_data[movie_title_key] = movie_payload
            
#             else: # برای فیلم‌های غیرسریالی
#                 qualities_data_for_movie = [] # لیست کیفیت‌ها برای این فیلم
                
#                 # گروه بندی بر اساس کیفیت برای فیلم‌های غیرسریالی
#                 # eq_for_movie_list از قبل بر اساس کیفیت مرتب شده
#                 for quality_value, eq_for_quality_iter in groupby(eq_for_movie_list, key=lambda eq: eq.quality):
#                     unique_episodes = {eq.episode.id: eq.episode for eq in eq_for_quality_iter}
#                     # sorted_episodes = sorted(list(unique_episodes.values()), key=lambda ep: ep.title)
#                     serialized_episodes = BasicEpisodeSerializer(list(unique_episodes.values()), many=True).data
                    
#                     # ساختار درخواستی برای هر کیفیت
#                     qualities_data_for_movie.append({
#                         quality_value: [{"episodes": serialized_episodes}]
#                     })
                
#                 # ساختار درخواستی برای فیلم غیرسریالی
#                 result_data[movie_title_key] = {"qualities": qualities_data_for_movie}
                
#         return Response(result_data)


class CombinedEpisodeQualityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BasicEpisodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        'episode__movie__title': ['icontains', 'exact'],
        'episode__movie__type': ['exact', 'in'],
        'episode__season': ['exact', 'isnull'],
        'quality': ['exact', 'in'],
        'episode__title': ['icontains'],
    }
    
    search_fields = [
        'episode__title', 
        'episode__movie__title', 
        'quality',
        'episode__slug'
    ]
    
    ordering_fields = [
        'episode__movie__title', 
        'episode__season', 
        'quality', 
        'episode__title',
        'episode__created_at'
    ]
    
    ordering = ['episode__movie__title', 'episode__movie__slug', 'episode__season', 'quality']

    def get_movie_instance(self, movie_identifier):
        """
        کمکی برای دریافت نمونه Movie بر اساس شناسه، اسلاگ یا عنوان.
        این تابع نمونه Polymorphic صحیح را برمی‌گرداند.
        """
        movie_queryset = Movie.objects.all() # ابتدا یک queryset پایه ایجاد می‌کنیم

        try:
            if isinstance(movie_identifier, int) or movie_identifier.isdigit():
                # برای دریافت نمونه واقعی با PK، بهتر است ابتدا فیلتر کنید و سپس get_real_instances
                # یا اگر مطمئن هستید که فقط یک نتیجه وجود دارد و می‌خواهید مستقیما نمونه واقعی را بگیرید:
                # return movie_queryset.get_real_instances(pk=int(movie_identifier)).first() # اگر get_real_instances مستقیما pk بگیرد
                # روش امن‌تر:
                instance = movie_queryset.filter(pk=int(movie_identifier)).first()
                if instance:
                    return instance.get_real_instance() # دریافت نمونه واقعی از یک آبجکت پایه
                return None
            
            # سپس با اسلاگ یا عنوان
            # ابتدا فیلتر می‌کنیم، سپس select_subclasses را روی queryset حاصله اعمال می‌کنیم
            filtered_queryset = movie_queryset.filter(
                Q(slug=movie_identifier) | Q(title=movie_identifier)
            )
            # select_subclasses باید روی queryset اعمال شود تا زیرکلاس‌ها را هم در نظر بگیرد
            movie = filtered_queryset.select_subclasses().first()
            return movie
        except Movie.DoesNotExist: # این استثنا معمولا با .first() رخ نمی‌دهد، اما برای اطمینان
            return None
        except ValueError: # اگر movie_identifier نتواند به int تبدیل شود و عددی هم نباشد
            # این بخش ممکن است تکراری با بلوک Q بالا باشد، اما برای پوشش حالت‌های مختلف نگه داشته شده
            filtered_queryset = movie_queryset.filter(
                Q(slug=movie_identifier) | Q(title=movie_identifier)
            )
            movie = filtered_queryset.select_subclasses().first()
            return movie
        except Exception: # برای خطاهای پیش‌بینی نشده دیگر
            # می‌توانید لاگ کنید یا مدیریت خطای بهتری انجام دهید
            return None

    # ... (بقیه متدهای کلاس get_queryset و list مانند قبل باقی می‌مانند)
    # فقط مطمئن شوید که در get_queryset و list از get_movie_instance استفاده می‌کنید
    # و سایر بخش‌های کد با این تغییرات سازگار هستند.

    def get_queryset(self):
        """
        Queryset پایه را بر اساس پارامترهای URL یا query params فیلتر می‌کند.
        """
        queryset = EpisodeQuality.objects.select_related(
            'episode',
            'episode__movie' 
        ).all()

        movie_identifier = self.kwargs.get('movie_slug')
        
        if not movie_identifier:
            movie_identifier = self.request.query_params.get('movie_slug') or \
                               self.request.query_params.get('movie_title') or \
                               self.request.query_params.get('movie_id')

        if movie_identifier:
            movie_instance = self.get_movie_instance(movie_identifier)

            if movie_instance:
                queryset = queryset.filter(episode__movie=movie_instance)
            else:
                return EpisodeQuality.objects.none() 
        
        return queryset

    # متد list بدون تغییر باقی می‌ماند، چون منطق دریافت movie_instance و queryset
    # در متدهای get_movie_instance و get_queryset انجام شده است.
    # فقط بخش مربوط به بررسی وجود فیلم برای خطای 404 در ابتدای متد list را مرور کنید
    # تا مطمئن شوید با خروجی get_movie_instance (که می‌تواند None باشد) به درستی کار می‌کند.

    def list(self, request, *args, **kwargs):
        movie_identifier_from_url = kwargs.get('movie_slug')
        movie_identifier_from_query = request.query_params.get('movie_slug') or \
                                      request.query_params.get('movie_title') or \
                                      request.query_params.get('movie_id')
        
        specific_movie_requested = bool(movie_identifier_from_url or movie_identifier_from_query)
        target_movie_identifier = movie_identifier_from_url or movie_identifier_from_query

        # اگر یک فیلم خاص درخواست شده، ابتدا بررسی می‌کنیم که آیا آن فیلم وجود دارد یا خیر
        # این کار قبل از اجرای get_queryset اصلی انجام می‌شود تا اگر فیلم وجود نداشت، سریعا 404 برگردانیم.
        if specific_movie_requested:
            movie_instance_check = self.get_movie_instance(target_movie_identifier)
            if not movie_instance_check:
                return Response({"detail": "فیلم یا سریال مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        # حالا queryset را بر اساس فیلم موجود (اگر مشخص شده) یا همه فیلم‌ها دریافت می‌کنیم
        queryset = self.filter_queryset(self.get_queryset())

        # اگر یک فیلم خاص درخواست شده بود و پس از فیلترها، queryset برای قسمت‌ها خالی است
        # (یعنی فیلم وجود دارد اما قسمتی ندارد)، لیست خالی برگردانده می‌شود که صحیح است.
        # خطای 404 برای "فیلم یافت نشد" قبلا مدیریت شده است.

        result_data = {}
        # گروه‌بندی اولیه بر اساس فیلم
        # اگر specific_movie_requested درست باشد، queryset فقط شامل داده‌های یک فیلم است.
        for movie_instance, eq_for_movie_iter in groupby(queryset, key=lambda eq: eq.episode.movie):
            movie_title_key = movie_instance.title 
            eq_for_movie_list = list(eq_for_movie_iter)

            if movie_instance.type == Type.SERIES:
                movie_payload = {}
                eq_for_movie_list.sort(key=lambda eq: (eq.episode.season is None, eq.episode.season))
                for season_number, eq_for_season_iter in groupby(eq_for_movie_list, key=lambda eq: eq.episode.season):
                    season_key = f"season-{season_number}" if season_number is not None else "season-0"
                    eq_for_season_list = list(eq_for_season_iter)
                    qualities_data_for_season = []
                    eq_for_season_list.sort(key=lambda eq: eq.quality)
                    for quality_value, eq_for_quality_iter in groupby(eq_for_season_list, key=lambda eq: eq.quality):
                        unique_episodes = {eq.episode.id: eq.episode for eq in eq_for_quality_iter}
                        serialized_episodes = BasicEpisodeSerializer(list(unique_episodes.values()), many=True).data
                        qualities_data_for_season.append({quality_value: [{"episodes": serialized_episodes}]})
                    movie_payload[season_key] = [{"qualities": qualities_data_for_season}]
                result_data[movie_title_key] = movie_payload
            else: 
                qualities_data_for_movie = []
                eq_for_movie_list.sort(key=lambda eq: eq.quality)
                for quality_value, eq_for_quality_iter in groupby(eq_for_movie_list, key=lambda eq: eq.quality):
                    unique_episodes = {eq.episode.id: eq.episode for eq in eq_for_quality_iter}
                    serialized_episodes = BasicEpisodeSerializer(list(unique_episodes.values()), many=True).data
                    qualities_data_for_movie.append({quality_value: [{"episodes": serialized_episodes}]})
                result_data[movie_title_key] = {"qualities": qualities_data_for_movie}
        
        # اگر یک فیلم خاص درخواست شده بود و هیچ داده‌ای برای آن در result_data نیست
        # (این حالت زمانی رخ می‌دهد که فیلم وجود دارد اما هیچ قسمت یا کیفیتی برای آن ثبت نشده)
        if specific_movie_requested and not result_data:
            # movie_instance_check از بررسی اولیه در ابتدای متد list در دسترس است
            # اگر به اینجا رسیده‌ایم، یعنی فیلم وجود دارد (movie_instance_check معتبر است)
            # اما هیچ قسمت یا کیفیتی برای آن در queryset نهایی نبوده.
            # در این حالت، result_data خالی برگردانده می‌شود که رفتار درستی است.
            pass

        return Response(result_data)