from django.conf.urls import url

from .views import TemplateVariableView

urlpatterns = [
    url(r'^(?P<template_type>[-\w]+)/$', TemplateVariableView.as_view(), name='template_variables'),
]
