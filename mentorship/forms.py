from django import forms

class MentorSearchForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)


class SendQuestionForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your question here...'}), max_length=1000)
