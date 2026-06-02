from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, StudentProfile, TeacherProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '¿Cuál es tu nombre de usuario?',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )


class StudentRegisterForm(forms.ModelForm):
    """Formulario para que los padres registren a sus hijos."""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Crea una contraseña segura'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Repite la contraseña'})
    )
    parent_name = forms.CharField(
        label='Tu nombre (mamá/papá/acudiente)',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del acudiente'})
    )
    parent_email = forms.EmailField(
        label='Tu correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'})
    )
    parent_phone = forms.CharField(
        label='Teléfono (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '300 000 0000'})
    )
    level = forms.ChoiceField(
        label='Nivel del niño/a',
        choices=StudentProfile.LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    age = forms.IntegerField(
        label='Edad del niño/a',
        min_value=3, max_value=7,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5'})
    )
    birth_date = forms.DateField(
        label='Fecha de nacimiento del niño/a',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        }),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    selected_avatar = forms.ChoiceField(
        label='Elige el avatar de tu niño/a',
        choices=StudentProfile.AVATAR_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'avatar-radio'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': 'Nombre del niño/a',
            'last_name': 'Apellido del niño/a',
            'username': 'Nombre de usuario (para ingresar)',
            'email': 'Correo electrónico del niño/a (opcional)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ejemplo: sofia2024'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'opcional'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                parent_name=self.cleaned_data['parent_name'],
                parent_email=self.cleaned_data['parent_email'],
                parent_phone=self.cleaned_data.get('parent_phone', ''),
                level=self.cleaned_data['level'],
                age=self.cleaned_data['age'],
                birth_date=self.cleaned_data['birth_date'],
                selected_avatar=self.cleaned_data['selected_avatar'],
            )
        return user


class TeacherRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    subject_specialty = forms.CharField(
        label='Especialidad',
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Preescolar, Arte...'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'teacher'
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                subject_specialty=self.cleaned_data.get('subject_specialty', '')
            )
        return user
