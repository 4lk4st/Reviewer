import os
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from dotenv import load_dotenv

load_dotenv()

User = get_user_model()

NAME_LEN = int(os.getenv('NAME_LEN'))
SLUG_LEN = int(os.getenv('SLUG_LEN'))


class Category(models.Model):
    """
    Model to represent a categories of titles.
    Ordering by slug field, descending.
    ...
    Attributes
    ----------
    name: str
        name of a category
    slug: str
        slug of a category

    Methods
    -------
    str():
        print a slug of a category.
    """
    name = models.CharField(max_length=NAME_LEN)
    slug = models.SlugField(max_length=SLUG_LEN, unique=True)

    def __str__(self):
        return f'{self.slug}'

    class Meta:
        ordering = ['-slug']


class Genre(models.Model):
    """
    Model to represent a genres of titles.
    Ordering by slug field, descending.
    ...
    Attributes
    ----------
    name: str
        name of a genre
    slug: str
        slug of a genre

    Methods
    -------
    str():
        print a slug of a genre.
    """
    name = models.CharField(max_length=NAME_LEN)
    slug = models.SlugField(max_length=SLUG_LEN, unique=True)

    def __str__(self):
        return f'{self.slug}'

    class Meta:
        ordering = ['-slug']


class Title(models.Model):
    """
    Model to represent a titles.
    Ordering by rating field, descending.
    ...
    Attributes
    ----------
    name: str
        name of a title
    year: int
        creation year of a title
    rating: int
        average rating of title from all reviews
    description: str
        description of a title
    genre: Genre
        genre of a title, link to genre model
    category: Category
        category of a title, link to category model

    Methods
    -------
    str():
        print a name of a title.
    """
    name = models.CharField(max_length=NAME_LEN)
    year = models.IntegerField()
    rating = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='titles')

    class Meta:
        ordering = ['-rating']

    def __str__(self):
        return f'{self.name}'[:10]


class Review(models.Model):
    """
    Model to represent a reviews on a titles.
    Ordering by publication date field, descending.
    ...
    Attributes
    ----------
    title: Title
        title, on which review was written
    text: str
        text of review
    author: User
        author of review
    score: int
        rating of title in current review
    pub_date: DateTime
        review's publication date

    Methods
    -------
    str():
        print a name of a title and score in this review.
    """
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Выберите произведение для отзывва')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка',
        help_text='Оцените произведение от 1 до 10'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления отзыва'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = (('title', 'author'),)

    def __str__(self) -> str:
        return f'Отзыв на произведение {self.title}. Оценка {self.score}'


class Comment(models.Model):
    """
    Model to represent a comments on a review.
    Ordering by publication date field, descending.
    ...
    Attributes
    ----------
    review: Review
        review, on which comment was written
    text: str
        text of comment
    author: User
        author of comment
    pub_date: DateTime
        review's publication date

    Methods
    -------
    str():
        print a name of review, on which comment was written.
    """
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',)
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления комментария'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'Комментарий на отзыв {self.review}'
