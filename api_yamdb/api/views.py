from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .permissions import IsAdmin, IsAdminOrReadOnly, ReviewCommentPermissions
from .serializers import (CategorySerializer, CommmentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer, UsersSerializer, UserTokenSerializer,
                          UserUpdateProfileSerializer)
from .viewsets import ListCreateDestroyViewSet
from .filter_fields import TitleFilter
from .service import generate_confirmation_code, send_confirmation_email


class UserViewSet(viewsets.ModelViewSet):
    '''Создание пользователя и получение confirmation_code'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    '''
    Мы пытались полностью убрать всю логику из вьюсета в сериализатор,
    впереписывали этот код и код сериализатора втроём по многу раз,
    но у нас каждый раз валились тесты, причем каждый раз - разные.
    Ниже решение, которое считаем самым сбалансированным,
    и с минимальным количеством строк из всех наших вариантов.
    '''

    def create(self, request, *args, **kwargs):
        # если такой юзер уже есть - то ничего в сериализатор не передаем,
        # только обновляем код подтверждения
        if User.objects.filter(username=request.POST.get("username"),
                               email=request.POST.get("email")).exists():
            user = User.objects.get(username=request.POST.get("username"),
                                    email=request.POST.get("email"))
            confirmation_code = generate_confirmation_code()
            user.confirmation_code = generate_confirmation_code()
            user.save()
            send_confirmation_email(user.email, confirmation_code)
            return Response(request.data, status=status.HTTP_200_OK)
        # в ином случае - передаем данные в сериализатор
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_200_OK,
                            headers=headers)


class CustomTokenObtainPairView(TokenObtainPairView):
    '''Получение токена'''
    serializer_class = UserTokenSerializer


class UserUpdateProfileAPIView(generics.RetrieveUpdateAPIView):
    '''Обновление информации о себе'''
    serializer_class = UserUpdateProfileSerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class UsersViewSet(viewsets.ModelViewSet):
    '''Обработка запросов от Администратора касательно пользователей'''
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermissions,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommmentSerializer
    permission_classes = (ReviewCommentPermissions,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer
