import csv
import io
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

DATAFOLDER = os.getcwd() + '//static//data//'


class Command(BaseCommand):
    help = "Импортирует информацию в БД из csv файлов в папке data"

    def handle(self, *args, **options):
        self.import_genres()
        self.import_categories()
        self.import_users()
        self.import_titles()
        self.import_reviews()

    def import_genres(self):
        with io.open(DATAFOLDER + 'genre.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                Genre.objects.get_or_create(name=row['name'], slug=row['slug'])

    def import_categories(self):
        with io.open(DATAFOLDER + 'category.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                Category.objects.get_or_create(name=row['name'],
                                               slug=row['slug'])

    def import_users(self):
        with io.open(DATAFOLDER + 'users.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                User.objects.get_or_create(id=row['id'],
                                           username=row['username'],
                                           email=row['email'],
                                           role=row['role'],
                                           bio=row['bio'],
                                           first_name=row['first_name'],
                                           last_name=row['last_name'])

    def import_titles(self):
        with io.open(DATAFOLDER + 'titles.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                Title.objects.get_or_create(
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category']))

        with io.open(DATAFOLDER + 'genre_title.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                genre = Genre.objects.get(id=row['genre_id'])
                Title.objects.get(id=row['title_id']).genre.add(genre)

    def import_reviews(self):
        with io.open(DATAFOLDER + 'review.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.get_or_create(title=title,
                                             text=row['text'],
                                             author=author,
                                             score=row['score'],
                                             pub_date=row['pub_date'])

    def import_comments(self):
        with io.open(DATAFOLDER + 'comments.csv', encoding='utf-8') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.get_or_create(review=review,
                                              text=row['text'],
                                              author=author,
                                              pub_date=row['pub_date'])
