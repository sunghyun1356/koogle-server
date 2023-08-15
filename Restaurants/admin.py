# from django.contrib import admin
# from .models import *
# # Register your models here.
# admin.site.register(Restaurant)
# admin.site.register(Menu_Detail)
# admin.site.register(Food)
# admin.site.register(Menu)
# admin.site.register(Restaurant_Food)
# admin.site.register(Category)
# admin.site.register(OpenHours)

from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('Restaurants')
# 딕셔너리를 사용하여 이미 등록된 모델과 관리자 클래스를 저장합니다.
registered_models = {}

for model_name, model in app.models.items():
    # 이미 등록된 모델인지 확인합니다.
    if model in registered_models:
        # 이미 등록된 경우 건너뜁니다.
        continue

    model_admin = type(model_name + "Admin", (admin.ModelAdmin,), {})

    model_admin.list_display = model.admin_list_display if hasattr(model, 'admin_list_display') else tuple([field.name for field in model._meta.fields])
    model_admin.list_filter = model.admin_list_filter if hasattr(model, 'admin_list_filter') else model_admin.list_display
    model_admin.list_display_links = model.admin_list_display_links if hasattr(model, 'admin_list_display_links') else ()
    model_admin.list_editable = model.admin_list_editable if hasattr(model, 'admin_list_editable') else ()
    model_admin.search_fields = model.admin_search_fields if hasattr(model, 'admin_search_fields') else ()

    admin.site.register(model, model_admin)

    # 모델과 관리자 클래스를 등록된 모델 딕셔너리에 추가합니다.
    registered_models[model] = model_admin
