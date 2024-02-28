"""
Defines helpers for validating e-mail templates
"""

from django.core.exceptions import ValidationError
from django.template import (  # TODO: should be able to specify engine
    Context,
    Template,
    TemplateSyntaxError,
)
from django.template.base import VariableNode
from django.utils.translation import gettext_lazy as _


class MailTemplateValidator(object):

    code = "invalid"

    def __init__(self, template):
        self.template = template
        self.config = template.config

    def validate(self, field):
        if not self.config:  # can't validate
            return
        template = self.check_syntax_errors(getattr(self.template, field))
        self.check_variables(template, field)

    def check_syntax_errors(self, value):
        try:
            return Template(value)
        except TemplateSyntaxError as exc:
            error_tpl = """
                <p>{{ error }}</p>

                {% if source %}
                    {{ source|linenumbers|linebreaks }}
                {% endif %}
            """
            if hasattr(exc, "django_template_source"):
                source = exc.django_template_source[0].source
                pz = exc.django_template_source[1]
                highlighted_pz = ">>>>{0}<<<<".format(source[pz[0] : pz[1]])
                source = "{0}{1}{2}".format(
                    source[: pz[0]], highlighted_pz, source[pz[1] :]
                )
                _error = _("TemplateSyntaxError: {0}").format(exc.args[0])
            elif hasattr(exc, "template_debug"):
                _error = _("TemplateSyntaxError: {0}").format(
                    exc.template_debug.get("message")
                )
                source = "{}".format(exc.template_debug.get("during"))
            else:
                _error = exc
                source = None
            error = Template(error_tpl).render(
                Context({"error": _error, "source": source})
            )
            raise ValidationError(error, code="syntax_error")

    def check_variables(self, template, field):
        variables_seen = set()
        required_vars = {var.name for var in self.config[field] if var.required}
        # TODO do we need to check optional_vars? the following line was here but never used
        # optional_vars = {var.name for var in self.config[field] if not var.required}
        for node in template.nodelist.get_nodes_by_type(VariableNode):
            var_name = node.filter_expression.var.var
            variables_seen.add(var_name)

        missing_vars = required_vars - variables_seen
        if missing_vars:
            attribute = self._is_attribute(variables_seen, required_vars)

            if not attribute:
                message = _("These variables are required, but missing: {vars}").format(
                    vars=self._format_vars(missing_vars)
                )
                raise ValidationError(
                    params={field: message}, message=message, code=self.code
                )

    def _is_attribute(self, var_names, known_vars):
        for var in var_names:
            if any(var.startswith("{}.".format(known_var)) for known_var in known_vars):
                return True

        return False

    def _format_vars(self, variables):
        return ", ".join("{{{{ {} }}}}".format(var) for var in variables)


def validate_template(mail_template):
    """
    Validate that the subject and body fields contain the expected variables.
    """
    validator = MailTemplateValidator(mail_template)
    errors = []
    for field in ["subject", "body"]:
        try:
            validator.validate(field)
        except ValidationError as error:
            errors.append(error)

    if errors:
        main_error = errors[0]
        if len(errors) > 1:
            for error in errors[1:]:
                main_error.update_error_dict(error.error_dict)
        raise main_error


class Variable(object):
    """
    A {{ template variable }}.

    The name of the variable is required. By default, the variable is optionally
    present in the mail template, but this can be enforced.
    """

    def __init__(self, name, description="", required=False, example=""):
        self.name = name
        self.description = description
        self.required = required
        self.example = example

    def get_html_list_item(self):
        variable_string = "<li>"
        if self.required:
            variable_string += "*"

        variable_string += "<b>{}</b>".format(self.name)

        if self.description:
            variable_string += ": <i>{}</i>".format(self.description)

        if self.example:
            variable_string += ' ("{}")'.format(self.example)

        variable_string += "</li>"
        return variable_string

    def __str__(self):
        return self.name
