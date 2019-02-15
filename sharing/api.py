from django.http import Http404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from sharing.serializers import OpenUrlSerializer, SharedLinkSerializer, SharedFileSerializer, SavedUrlSerializer
from sharing.models import SharedUrl, SharedLink, SharedFile


class AddItem(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = None  # this is an abstract class,

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        new_url = SharedUrl(author=request.user)
        new_url.save()
        serializer.save(url=new_url)
        return Response(SavedUrlSerializer(new_url).data)


class AddLink(AddItem):
    serializer_class = SharedLinkSerializer


class AddFile(AddItem):
    parser_classes = (MultiPartParser,)
    serializer_class = SharedFileSerializer


class Open(APIView):
    def post(self, request, url=None):
        serializer = OpenUrlSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        passwd = serializer.validated_data['password']
        shared_url = SharedUrl.objects.get(url=url)
        if shared_url.check_password(passwd):
            if hasattr(shared_url, 'shared_link'):
                return Response(shared_url.shared_link.link)
            if hasattr(shared_url, 'shared_file'):
                return Response(shared_url.shared_file.file.url)
            else:
                return Response(f'No item for url {repr(shared_url)}', status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response('bad password', status=status.HTTP_401_UNAUTHORIZED)


class Stats(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        result = {}
        days = SharedUrl.objects.filter(author=request.user).dates('created', 'day')
        for d in days.all():
            links = SharedLink.objects.filter(url__author=request.user, url__created__date=d, url__views__gt=0)
            files = SharedFile.objects.filter(url__author=request.user, url__created__date=d, url__views__gt=0)
            result[str(d)] = {
                    'links': links.count(),
                    'files': files.count()
                    }
        return Response(result)
