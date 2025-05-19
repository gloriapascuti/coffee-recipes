from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models.coffee import Coffee, Origin
from .models.uploads import UploadedFile
from .models import UserProfile

@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Coffee)
class CoffeeAdmin(admin.ModelAdmin):
    list_display        = ('id', 'name', 'origin')
    list_select_related = ('origin',)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')

admin.site.register(UserProfile)
