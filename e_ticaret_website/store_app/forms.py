from .models import Review
from django import forms

# Review form
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')

        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
