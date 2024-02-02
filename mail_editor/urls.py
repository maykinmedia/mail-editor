from django.conf.urls import url

from .views import TemplateBrowserPreviewView, TemplateVariableView

# Add app_name to support django 2.0+
app_name = "mail_editor"

# Mostly empty as URLs moved to ModelAdmin.get_urls()
urlpatterns = [
]
