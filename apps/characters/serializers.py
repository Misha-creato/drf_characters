from rest_framework import serializers

from characters.models import Character


class CharacterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'image',
            'hp',
            'attack',
            'speed',
            'level',
        ]


class CharacterIDSerializer(serializers.Serializer):
    characters_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1)
    )
