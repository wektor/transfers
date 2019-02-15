from rest_framework import serializers

from sharing.models import SharedUrl, SharedLink, SharedFile


class OpenUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedUrl
        fields = ['password']


class SavedUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedUrl
        fields = ['url', 'full_url', 'password']


class SharedLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedLink
        fields = ['link']


class SharedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedFile
        fields = ['file']


