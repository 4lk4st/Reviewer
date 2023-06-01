# from email.policy import default

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email")
        model = User


class UserTokenSerializer(TokenObtainPairSerializer):
    confirmation_code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        # Проверка confirmation_code на соответствие условиям
        if user.confirmation_code == confirmation_code:
            attrs.update({'password': ''})
            token = RefreshToken.for_user(user)
            return {'token': str(token.access_token)}
        else:
            print(f'пользователя: {user.confirmation_code}')
            print(f'в запросе: {confirmation_code}')
            raise serializers.ValidationError('Invalid confirmation code')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name", "last_name", "bio",
                  "role")
        model = User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name", "last_name", "bio",
                  "role")
        model = User

    def create(self, validated_data):
        role = validated_data.get('role', Group.objects.get(name='user'))
        validated_data['role'] = role
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='id', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        author = self.context['request'].user
        title_id = self.context.get('view').kwargs.get('title_id')
        if (
            self.context['request'].method == 'POST'
            and Review.objects.filter(author=author, title=title_id).exists()
        ):
            raise serializers.ValidationError('Вы уже написали свой отзыв!')
        return data


class CommmentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    review = serializers.SlugRelatedField(
        read_only=True, slug_field='id')

    class Meta:
        fields = '__all__'
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'year',
                  'rating', 'genre', 'category')

    def get_rating(self, obj):
        review_list = Review.objects.filter(title__id=obj.id)
        if len(review_list) != 0:
            score_list = [i.score for i in review_list]
            return sum(score_list) / len(score_list)
        return None


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'year',
                  'rating', 'genre', 'category')
