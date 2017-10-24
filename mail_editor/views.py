from django.http import HttpResponse
from django.views.generic import View

from .utils import variable_help_text


class TemplateVariableView(View):
    def get(self, request, *args, **kwargs):
        variables = variable_help_text(kwargs.get('template_type'))
        return HttpResponse(variables)
