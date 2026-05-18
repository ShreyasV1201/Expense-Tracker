# forms.py
from django import forms
from .models import Expense, Income, Profile
from .models import Recurring_expenses

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'description']
        widgets = { 
            'date':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Food, Transport'}),
            'amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional details...'}),
        }

class IncomeForm(forms.ModelForm):  
    class Meta:
        model  = Income
        fields = ['date', 'category', 'amount', 'description']
        widgets = {
            'date':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Salary, Gift'}),
            'amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional details...'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        # keep the same order as your model
        fields = ['user', 'first_name', 'last_name', 'mobile', 'address']
        widgets = {
            # we keep user hidden (it will be set in the view)
            'user':       forms.HiddenInput(),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'mobile':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123-456-7890'}),
            'address':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, City, …'}),
        }

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = Recurring_expenses
        fields = [
            'amount',
            'frequency',
            'start_date',
            'end_date',
            'description',
            'status',
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'amount': 'Amount',
            'frequency': 'Frequency',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'description': 'Description',
            'status': 'Status',
        }

    def clean_end_date(self):
        start = self.cleaned_data.get('start_date')
        end = self.cleaned_data.get('end_date')
        if end and start and end < start:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        return end
