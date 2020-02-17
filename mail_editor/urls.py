from django.conf.urls import url

from .views import TemplateVariableView

# Add app_name to support django 2.0+
app_name = "mail_editor"

urlpatterns = [
    url(r'^(?P<template_type>[-\w]+)/$', TemplateVariableView.as_view(), name='template_variables'),
]
