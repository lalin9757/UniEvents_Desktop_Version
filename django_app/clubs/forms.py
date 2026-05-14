from django import forms
from .models import Club, ClubMember, ClubCategory

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            'name', 'category', 'description', 'short_description',
            'logo', 'banner', 'email', 'website',
            'social_facebook', 'social_instagram', 'social_linkedin'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }

class ClubMemberForm(forms.ModelForm):
    class Meta:
        model = ClubMember
        fields = ['role', 'additional_info']

class JoinClubForm(forms.Form):
    reason = forms.CharField(
        label="Why do you want to join this club?",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your interests and why you want to join...'}),
        required=True,
        help_text="Explain your motivation for joining."
    )

class ClubCategoryForm(forms.ModelForm):
    class Meta:
        model = ClubCategory
        fields = ['name', 'description', 'icon']