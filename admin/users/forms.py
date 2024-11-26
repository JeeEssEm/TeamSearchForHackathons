from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import Form, EmailField


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            User.username.field.name,
            User.email.field.name,
            User.first_name.field.name,
            User.last_name.field.name
        )


class LoginForm(AuthenticationForm):
    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя/email'


class ResendActivationForm(Form):
    email = EmailField(required=True)
