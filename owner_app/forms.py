from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from staff_app.models import StationStaffProfile


class StationStaffCreateForm(forms.Form):
    station = forms.ModelChoiceField(queryset=None)
    full_name = forms.CharField(max_length=100)
    employee_id = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.fields['station'].queryset = owner.evstation_set.order_by('station_name')
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already in use.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        if password and password != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        if password:
            candidate = User(
                username=cleaned.get('username', ''),
                email=cleaned.get('email', ''),
            )
            try:
                validate_password(password, candidate)
            except ValidationError as error:
                self.add_error('password', error)

        station = cleaned.get('station')
        employee_id = cleaned.get('employee_id')
        if station and employee_id and StationStaffProfile.objects.filter(
            station=station,
            employee_id__iexact=employee_id,
        ).exists():
            self.add_error('employee_id', 'That employee ID already exists at this station.')
        return cleaned

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
        )
        return StationStaffProfile.objects.create(
            user=user,
            station=self.cleaned_data['station'],
            created_by=self.owner,
            full_name=self.cleaned_data['full_name'],
            employee_id=self.cleaned_data['employee_id'],
            phone=self.cleaned_data['phone'],
        )
