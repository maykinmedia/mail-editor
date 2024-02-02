from django.conf.urls import url

from .views import TemplateBrowserPreviewView, TemplateVariableView

# Add app_name to support django 2.0+
app_name = "mail_editor"

urlpatterns = [
    url(r'^(?P<template_type>[-\w]+)/variables/$', TemplateVariableView.as_view(), name='template_variables'),
    url(r'^(?P<pk>[0-9]+)/preview/$', TemplateBrowserPreviewView.as_view(), name='template_preview'),
]
