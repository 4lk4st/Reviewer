from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters

from reviews.models import Category, Genre, Review, Title
from users.models import User
from users.permissions import create_roles_and_permissions

from .permissions import IsAdmin, IsAdminOrReadOnly, ReviewCommentPermissions
from .serializers import (CategorySerializer, CommmentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer, UsersSerializer, UserTokenSerializer,
                          UserUpdateProfileSerializer)
from .service import generate_confirmation_code, send_confirmation_email
from .viewsets import ListCreateDestroyViewSet
from .filter_fields import TitleFilter

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    '''Создание пользователя и получение confirmation_code'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        create_roles_and_permissions()
        if (
            User.objects.filter(username=username).exists()
            and User.objects.get(username=username).email != email
        ):
            raise ValidationError(
                {'username': 'email не соответствует данному пользователю.'},
                code=status.HTTP_400_BAD_REQUEST)
        existing_user = User.objects.filter(username=username).first()
        # Проверяем есть ли такой пользователь, если да то отдаем ему код
        if existing_user:
            confirmation_code = generate_confirmation_code()
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
            send_confirmation_email(email, confirmation_code)
            return Response({'message': 'Confirmation code sent'},
                            status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Отправляем код подтверждения после создания пользователя
        user = serializer.instance
        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_email(user.email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save()


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
        if 'role' in request.data:
            current_role = self.request.user.role
            new_role = request.data.get('role')
            if current_role != new_role:
                return Response(
                    {'detail': 'Вы не можете изменить свою роль'},
                    status=status.HTTP_403_FORBIDDEN
                )
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

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        errors = {}
        if not email:
            errors['email'] = ['Поле email обязательно для заполнения.']
        if not username:
            errors['username'] = ['Поле username обязательно для заполнения.']
        if User.objects.filter(email=email).exists():
            errors['email'] = ['Пользователь с таким email уже зарегистрирован'
                               'и не соответствует данному username.']
        if errors:
            raise ValidationError(errors)
        return super().create(request, *args, **kwargs)


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
