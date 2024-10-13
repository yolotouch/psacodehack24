from django import forms

class EmployeeForm(forms.Form):
    current_role = forms.CharField(label='Current Role', max_length=100)
    career_goal = forms.CharField(label='Career Goal', max_length=100)
    current_skillset = forms.CharField(widget=forms.Textarea, label='Current Skillset (comma-separated)')

class TrendAnalysisForm(forms.Form):
    default_urls = (
        'https://www.mckinsey.com/industries/travel-logistics-and-infrastructure/our-insights/the-future-of-automated-ports'
    )
    
    urls = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        label='Enter URLs (one per line)',
        initial=default_urls,  # Prepopulate URLs
        required=False
    )

