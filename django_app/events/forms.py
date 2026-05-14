from django import forms
from django.utils import timezone
from .models import Event, EventRegistration, EventCategory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'category', 'event_type', 'description', 'short_description',
            'start_date', 'end_date', 'venue', 'location_map',
            'banner', 'featured_image', 'max_participants',
            'is_free', 'fee', 'registration_open', 'registration_close',
            'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_open': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_close': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_close = cleaned_data.get('registration_close')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")

        if registration_close and start_date and registration_close >= start_date:
            raise forms.ValidationError(
                f"Registration deadline must be before the event start date "
                f"({start_date.strftime('%b %d, %Y %I:%M %p')}). "
                f"Students must register before the event begins."
            )

        if registration_close and end_date and registration_close > end_date:
            raise forms.ValidationError("Registration deadline cannot be after the event end date.")

        return cleaned_data

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['additional_info']

class EventCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = ['name', 'icon', 'color']

class EventFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    event_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Event.EVENT_TYPE_CHOICES),
        required=False
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )