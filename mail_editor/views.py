from django.http import HttpResponse
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from .models import MailTemplate
from .utils import variable_help_text


class TemplateVariableView(View):
    def get(self, request, *args, **kwargs):
        variables = variable_help_text(kwargs['template_type'])
        return HttpResponse(variables)


class TemplateBrowserPreviewView(SingleObjectMixin, View):
    model = MailTemplate

    def get(self, request, *args, **kwargs):
        template = self.get_object()
        subject_ctx, body_ctx = template.get_preview_contexts()

        subject, body = template.render(body_ctx, subject_ctx)
        return HttpResponse(body, content_type="text/html")
