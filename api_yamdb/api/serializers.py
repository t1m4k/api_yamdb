from rest_framework import serializers
from reviews.models import Review, Comment


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    def create(self, validated_data):
        if Review.objects.filter(
            author=self.context['request'].user, 
            title=self.validated_data.get('title')).exists:
            raise serializers.ValidationError(
                'Возможно оставить только один обзор'
            )
        return  Review.objects.create(**validated_data)

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Comment