from django.contrib import admin
# Register your models here.
from .models import Result, AI_Model
from . import models

#todo 관리에서 Result 객체에 대해  기본 CRUD 관리를 한다.
admin.site.register(Result)
# admin.site.register(ModelList)

@admin.register(models.AI_Model)
class showModels(admin.ModelAdmin):
    list_display = (
        "model_Name",
        "model_Version", 
        "model_File",
        "is_selected",
        "create_Date"
    )
