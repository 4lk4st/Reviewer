from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, CustomTokenObtainPairView,
                    GenreViewSet, ReviewViewSet, TitleViewSet, UsersViewSet,
                    UserUpdateProfileAPIView, UserViewSet)


router_v1 = DefaultRouter()

router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/auth/signup/',
         UserViewSet.as_view({'post': 'create'}),
         name='user-signup'),
    path('v1/auth/token/',
         CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/users/me/',
         UserUpdateProfileAPIView.as_view(),
         name='user-update-profile'),

    path('v1/', include(router_v1.urls)),
]
