from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("maileditor/", include("mail_editor.urls")),
    path("admin/", admin.site.urls),
]
