from django.utils.safestring import mark_safe

from .settings import get_config


def variable_help_text(template_type):
        subject_html = '<ul>'
        body_html = '<label>Body variables:</label> <ul>'

        template_conf = get_config().get(template_type)
        if template_conf:
            subject_variables = template_conf.get('subject')
            body_variables = template_conf.get('body')

            if subject_variables:
                for variable in subject_variables:
                    subject_html += variable.get_html_list_item()

            if body_variables:
                for variable in body_variables:
                    body_html += variable.get_html_list_item()

        subject_html += '</ul>'
        body_html += '</ul>'

        return mark_safe('{}<br><br>{}'.format(subject_html, body_html))
