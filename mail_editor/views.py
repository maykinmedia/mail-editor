from django import forms
from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView

from .models import MailTemplate
from .process import process_html
from .settings import settings
from .utils import variable_help_text


class TemplateVariableView(View):
    def get(self, request, *args, **kwargs):
        variables = variable_help_text(kwargs["template_type"])
        return HttpResponse(variables)


class TemplateBrowserPreviewView(SingleObjectMixin, View):
    model = MailTemplate

    def get(self, request, *args, **kwargs):
        template = self.get_object()
        subject_ctx, body_ctx = template.get_preview_contexts()

        _subject, body = template.render(body_ctx, subject_ctx)
        body, _attachments = process_html(
            body, settings.BASE_HOST, extract_attachments=False
        )
        return HttpResponse(body, content_type="text/html")


class TemplateEmailPreviewForm(forms.Form):
    recipient = forms.EmailField(label=_("Recipient"), required=True)


class TemplateEmailPreviewFormView(FormView, DetailView):
    model = MailTemplate
    form_class = TemplateEmailPreviewForm
    context_object_name = "template"
    template_name = "admin/mail_editor/preview_form.html"

    def form_valid(self, form):
        recipient = form.cleaned_data["recipient"]
        subject_ctx, body_ctx = self.object.get_preview_contexts()

        result = self.object.send_email([recipient], body_ctx, subj_context=subject_ctx)

        if result:
            messages.success(
                self.request, _("Email sent to {email}").format(email=recipient)
            )
        else:
            messages.warning(
                self.request, _("Email not sent to {email}").format(email=recipient)
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # context to make the (remaining parts of the) admin template work
        ctx.update(admin.site.each_context(self.request))
        ctx.update(
            {
                "opts": self.model._meta,
                "original": self.object,
                "title": "{} {}".format(self.model._meta.verbose_name, _("preview")),
            }
        )

        subject_ctx, body_ctx = self.object.get_preview_contexts()
        subject, _body = self.object.render(body_ctx, subject_ctx)
        # our own context data
        ctx.update(
            {
                "subject": subject,
                "render_url": reverse(
                    "admin:mailtemplate_render", kwargs={"pk": self.object.id}
                ),
            }
        )
        return ctx

    def get_success_url(self):
        return reverse("admin:mailtemplate_preview", kwargs={"pk": self.object.id})

    def get(self, request, *args, **kwargs):
        # mixing FormView and DetailView
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # mixing FormView and DetailView
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
