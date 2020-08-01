from wtforms import (
    Form,
    BooleanField,
    StringField,
    validators,
    SelectMultipleField,
    ValidationError,
    widgets,
    HiddenField,
    SubmitField,
    PasswordField,
)
import flask
from wtforms.csrf.session import SessionCSRF
from . import app


def bootstrap(cls):
    class Wrapper:
        def __init__(self, error_class=u"is-invalid"):
            self.instance = cls()
            self.error_class = error_class

        def __call__(self, field, **kwargs):
            c = kwargs.pop("class", "").split(" ") or kwargs.pop("class_", "").split(
                " "
            )

            c.append("form-control")

            if field.errors:
                # kwargs['class'] = u'%s %s' % (self.error_class, c)
                c.append(self.error_class)

            kwargs["class"] = " ".join(c)
            # return super(BootstrapInput, self).__call__(field, **kwargs)
            return self.instance.__call__(field, **kwargs)

    return Wrapper


@bootstrap
class TextInput(widgets.TextInput):
    pass
    # def __init__(self, error_class=u'is-invalid'):
    # super(BootstrapInput, self).__init__()
    # self.error_class = error_class

    # def __call__(self, field, **kwargs):
    # c = kwargs.pop('class', '') or kwargs.pop('class_', '').split(" ")

    # c.append("form-control")

    # if field.errors:
    # # kwargs['class'] = u'%s %s' % (self.error_class, c)
    # c.append(self.error_class)

    # kwargs['class'] = " ".join(c)
    # return super(BootstrapInput, self).__call__(field, **kwargs)


@bootstrap
class PasswordInput(widgets.PasswordInput):
    pass


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config["CSRF_SECRET_KEY"]

        @property
        def csrf_context(self):
            return flask.session


class LoginForm(BaseForm):
    email = StringField(
        "E-Mail",
        [validators.Length(min=4), validators.DataRequired()],
        widget=TextInput(),
    )
    password = PasswordField(
        "Password",
        [validators.Length(min=4), validators.DataRequired()],
        widget=PasswordInput(),
    )


class RegisterForm(BaseForm):
    email = StringField(
        "E-Mail",
        [validators.Length(min=4), validators.DataRequired()],
        widget=TextInput(),
    )
    password = PasswordField(
        "Password",
        [validators.Length(min=4), validators.DataRequired()],
        widget=PasswordInput(),
    )
    password2 = PasswordField(
        "Password confirmation",
        [validators.Length(min=4), validators.DataRequired()],
        widget=PasswordInput(),
    )
    gdpr1 = BooleanField(
        "E-Mail and Password",
        [validators.DataRequired(message="You must accept before registering")],
        description="I agree that this service stores my email address and password indefinitely, to allow me to log in. The password is stored using industry standard hashing.",
        default=False,
    )

    gdpr2 = BooleanField(
        "Server logs",
        [validators.DataRequired(message="You must accept before registering")],
        description="I agree that this service stores basic server logs containing my IP address for the purpose of diagnosing application behaviour and performance. Logs are deleted after 60 days.",
        default=False,
    )

    def validate(self):
        if not super().validate():
            return False

        if self.password.data != self.password2.data:
            self.password2.errors.append("Passwords must match")
            return False

        return True


class CalendarForm(BaseForm):
    name = StringField(
        "Name",
        [validators.Length(min=3), validators.DataRequired()],
        widget=TextInput(),
    )


class CalendarSourceForm(BaseForm):
    url = StringField(
        "URL", [validators.URL(), validators.DataRequired()], widget=TextInput()
    )
    positive_pattern = StringField("Positve pattern", default=".*", widget=TextInput())
    negative_pattern = StringField("Negative pattern", widget=TextInput())
    alerts = StringField("Alerts", default="15", widget=TextInput())

    # def validate_alerts(form, field):
    # if not(all(map(is_int, field.data))):
    # raise ValidationError("Alerts must be integers")


class DeleteForm(BaseForm):
    pass


class EditForm(BaseForm):
    pass


class LogoutForm(BaseForm):
    pass
