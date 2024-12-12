from django.forms import Form, CharField


class CreateTechnologyForm(Form):
    title = CharField(label='Название технологии', max_length=100)
