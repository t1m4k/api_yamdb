from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='category', null=True
    )

    class Meta:
        ordering = ('id',)


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Автор отзыва')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews', verbose_name='Произведение')
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Оценка произведения')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)
        constraints = [models.UniqueConstraint(
            fields=['author', 'title'],
            name='only_one_review_for_each_title')
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments', verbose_name='Ревью')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)
