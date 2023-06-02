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
    """
    Serializer for a User model
    ...
    Attributes
    ----------
    username: str
        name of a user
    email: str
        email of a user
    """
    class Meta:
        fields = ("username", "email")
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                {'username': 'Нельзя использовать "me" для username'})
        return value


class UserTokenSerializer(TokenObtainPairSerializer):
    """
    Serializer for a user's token
    ...
    Methods
    ----------
    init():
        redefine super().init method
        to make password requirement optional
    validate():
        check confirmation code and password update
    """
    confirmation_code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if user.confirmation_code == confirmation_code:
            attrs.update({'password': ''})
            token = RefreshToken.for_user(user)
            return {'token': str(token.access_token)}
        else:
            print(f'пользователя: {user.confirmation_code}')
            print(f'в запросе: {confirmation_code}')
            raise serializers.ValidationError('Invalid confirmation code')


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for a user's Group model
    ...
    Attributes
    ----------
    id: int
        id of a user's group
    name: str
        name of a user's group
    """
    class Meta:
        model = Group
        fields = ('id', 'name')


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for a user's profile update
    ...
    Attributes
    ----------
    username: str
        name of a user
    email: str
        email of a user
    first_name: str
        first name of a user
    last_name: str
        last name of a user
    bio: str
        biography of a user
    """
    class Meta:
        fields = ("username", "email", "first_name", "last_name", "bio",
                  "role")
        model = User


class UsersSerializer(serializers.ModelSerializer):
    """
    Serializer for a User model
    ...
    Attributes
    ----------
    username: str
        name of a user
    email: str
        email of a user
    first_name: str
        first name of a user
    last_name: str
        last name of a user
    bio: str
        biography of a user

    Methods
    -------
    create():
        validate a role of a user with Group model
    """
    class Meta:
        fields = ("username", "email", "first_name", "last_name", "bio",
                  "role")
        model = User

    def create(self, validated_data):
        role = validated_data.get('role', Group.objects.get(name='user'))
        validated_data['role'] = role
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for a Review model
    ...
    Attributes
    ----------
    title: Title
        link of a title, on which review was written
    author: User
        link of a user, which write a review

    Methods
    -------
    validate():
        check if user already create a review on current title
    """
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
    """
    Serializer for a Comment model
    ...
    Attributes
    ----------
    author: User
        link to user, which write a comment
    review: Review
        link to review, that a comment was written on
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    review = serializers.SlugRelatedField(
        read_only=True, slug_field='id')

    class Meta:
        fields = '__all__'
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for a Category model
    ...
    Attributes
    ----------
    name: str
        name of a category
    slug: str
        slug of a category
    """
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for a Genre model
    ...
    Attributes
    ----------
    name: str
        name of a genre
    slug: str
        slug of a genre
    """
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Serializer for GET or RETRIEVE methods on Title model
    ...
    Attributes
    ----------
    genre: Genre
        link to genre's serializer
    category: Category
        link to category's serializer
    rating: int
        average rating of a title

    Methods
    -------
    get_rating():
        gather all scores from all reviews for this title
        and calculate average
    """
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
    """
    Serializer for POST, PATH or DELETE methods on Title model
    ...
    Attributes
    ----------
    id: int
        id of a title
    name: str
        name of a title
    year: int
        creation year of a title
    rating: int
        average rating of title from all reviews
    description: str
        description of a title
    genre: Genre
        link to genre's serializer
    category: Category
        link to category's serializer
    """
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
