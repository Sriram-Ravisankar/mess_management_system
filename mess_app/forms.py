from django import forms # type: ignore
from .models import LeaveRequest, Feedback, LostAndFound, MealRating

# --- Leave Request Form ---

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['from_date', 'to_date', 'reason']
        widgets = {
            # Use HTML5 date input type
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

# --- Feedback Form (RATING FIELD REMOVED) ---

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        # FIX: Only include the 'comment' field
        fields = ['comment'] 
        widgets = {
            # Ensure visible rows for the textarea
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
    # Overriding fields to use radio buttons for the score and exclude the date/student
    rating_score = forms.ChoiceField(
        choices=MealRating.RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Rating Score'
    )

    class Meta:
        model = MealRating
        # meal_type is hidden, rating_date is defaulted in view
        fields = ['meal_type', 'rating_score', 'comment']
        widgets = {
            'meal_type': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 2, 'class': 'form-textarea', 'placeholder': 'Optional: Add your specific feedback here...'}),
        }