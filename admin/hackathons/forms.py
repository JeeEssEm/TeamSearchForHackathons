from django.forms import Form, DateField, CharField, DateInput, ValidationError


class HackathonForm(Form):
    title = CharField(label='Название хакатона', required=True)
    start_date = DateField(label='Дата начала', required=True,
                           widget=DateInput(attrs={'type': 'date'}))
    end_date = DateField(label='Дата окончания', required=True,
                         widget=DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date > end_date:
            raise ValidationError(
                'Дата начала не может быть больше даты окончания'
            )
        return cleaned_data
