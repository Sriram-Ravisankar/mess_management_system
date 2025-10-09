from django import forms # type: ignore
from .models import LeaveRequest, Feedback, LostAndFound, MealRating

# --- Leave Request Form ---

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['from_date', 'to_date', 'reason']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        reason = cleaned_data.get('reason')

        # Mandatory Validation for Reason
        if not reason or len(reason.strip()) < 5:
            self.add_error('reason', 'Reason for leave is mandatory and must be descriptive.')

        # Date validation
        if from_date and to_date:
            if from_date > to_date:
                self.add_error('to_date', 'To Date cannot be before From Date.')

        return cleaned_data

# --- Feedback Form  ---

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment'] 
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
        }

# --- Lost & Found Form (Student reporting) ---

class LostAndFoundForm(forms.ModelForm):
    class Meta:
        model = LostAndFound
        fields = ['type', 'item_name', 'date_event', 'place_event', 'description']
        widgets = {
            'date_event': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }

# --- Meal Rating Form (NEW) ---

class MealRatingForm(forms.ModelForm):
    rating_score = forms.ChoiceField(
        choices=MealRating.RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Rating Score'
    )

    class Meta:
        model = MealRating
        fields = ['meal_type', 'rating_score', 'comment']
        widgets = {
            'meal_type': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 2, 'class': 'form-textarea', 'placeholder': 'Optional: Add your specific feedback here...'}),
        }