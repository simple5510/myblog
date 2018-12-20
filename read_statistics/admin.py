from django.contrib import admin
from .models import  ReadNum,ReadDetails
# Register your models here.
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num','content_type')

@admin.register(ReadDetails)
class ReadDetailsAdmin(admin.ModelAdmin):
    list_display = ('date','read_num', 'content_type')