from django.forms import CharField, Form, Textarea


class QuestionaryForm(Form):
    feedback = CharField(widget=Textarea, required=False)
