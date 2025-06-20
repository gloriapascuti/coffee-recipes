from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models.coffee import Coffee, Origin
from .models.uploads import UploadedFile
from .models.coffee_operations import CoffeeOperation
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

@admin.register(CoffeeOperation)
class CoffeeOperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'operation_type', 'coffee_name', 'coffee_id', 'timestamp')
    list_filter = ('operation_type', 'timestamp')
    list_select_related = ('user',)
    ordering = ('-timestamp',)

admin.site.register(UserProfile)
