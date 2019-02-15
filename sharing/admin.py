from django.contrib import admin
from sharing.models import SharedLink, SharedFile, SharedUrl, User


admin.site.register(SharedUrl)
admin.site.register(SharedLink)
admin.site.register(SharedFile)
admin.site.register(User)
