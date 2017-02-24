from django.utils.safestring import mark_safe

from mail_editor import settings


def variable_help_text(template_type):
        subject_html = 'Subject: <br><ul>'
        body_html = 'Body: <br><ul>'

        template_conf = settings.get_config().get(template_type)
        if template_conf:
            subject_variables = template_conf.get('subject')
            body_variables = template_conf.get('body')

            if subject_variables:
                for variable in subject_variables:
                    if variable.required:
                        subject_html += '<li>* {}</li>'.format(variable.name)
                    else:
                        subject_html += '<li>{}</li>'.format(variable.name)

            if body_variables:
                for variable in body_variables:
                    if variable.required:
                        body_html += '<li>* {}</li>'.format(variable.name)
                    else:
                        body_html += '<li>{}</li>'.format(variable.name)

        subject_html += '</ul>'
        body_html += '</ul>'

        return mark_safe('{}<br><br>{}'.format(subject_html, body_html))
