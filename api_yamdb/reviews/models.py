from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.slug}'

    class Meta:
        ordering = ['-slug']


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.slug}'

    class Meta:
        ordering = ['-slug']


class Title(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    rating = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='titles')

    class Meta:
        ordering = ['-rating']

    def __str__(self):
        return f'{self.name}'[:10]


class Review(models.Model):
    """Модель отзывов"""
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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'),
        ]

    def __str__(self) -> str:
        return f'Отзыв на произведение {self.title}. Оценка {self.score}'


class Comment(models.Model):
    """Модель комментариев."""
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
