from django import forms 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import authenticate 
from .models import LeaveRequest, Feedback, LostAndFound, MealRating

# ---Login Form (Allows Email or Username) ---

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that allows login using either username or email.
    """
    username = forms.CharField(
        label="Username or Email",
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        self.user_cache = None 
        
        if username and password:
            if '@' in username:
                try:
                    user_model = self.get_user_model()
                    user = user_model.objects.get(email__iexact=username)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except user_model.DoesNotExist:
                    pass 

            # --- 2. Fallback to Standard Username Authentication ---
            if self.user_cache is None:
                self.user_cache = authenticate(self.request, username=username, password=password)

            # --- 3. Final Validation and Confirmation ---
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            self.confirm_user_is_active() 
        
        return self.cleaned_data
    
    def confirm_user_is_active(self):
        """
        Confirms the user is active, required by the base AuthenticationForm.
        """
        if not self.user_cache.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_model(self):
        from django.contrib.auth import get_user_model
        return get_user_model()


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

# --- Feedback Form ---

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment'] 
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
        }

# --- Lost & Found Form ---

class LostAndFoundForm(forms.ModelForm):
    class Meta:
        model = LostAndFound
        fields = ['type', 'item_name', 'date_event', 'place_event', 'description']
        widgets = {
            'date_event': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }

# --- Meal Rating Form ---

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