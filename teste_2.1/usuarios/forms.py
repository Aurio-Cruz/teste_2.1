import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from usuarios.models import Perfil

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

class UsuarioForm(forms.ModelForm):
    nome_empresa = forms.CharField(max_length=100, required=True)
    email_empresa = forms.EmailField(required=True)
    telefone = forms.CharField(max_length=15, required=True)
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    last_name = forms.CharField(max_length=150, required=True)
    repita_email_pessoal = forms.EmailField(label="Repita Email-pessoal", required=True)
    repita_email_empresa = forms.EmailField(label="Repita Email da empresa", required=True)

    class Meta:
        model = User
        fields = ["username", "email", "telefone", "last_name"]
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'off'}),
            'telefone': forms.TextInput(attrs={'autocomplete': 'off'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email_pessoal = cleaned_data.get('email')
        repita_email_pessoal = cleaned_data.get('repita_email_pessoal')
        email_empresa = cleaned_data.get('email_empresa')
        repita_email_empresa = cleaned_data.get('repita_email_empresa')

        if email_pessoal != repita_email_pessoal:
            self.add_error('repita_email_pessoal', "Os emails pessoais não coincidem.")
        
        if email_empresa != repita_email_empresa:
            self.add_error('repita_email_empresa', "Os emails da empresa não coincidem.")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está registrado.")
        return email

    def clean_telefone(self):
        telefone = self.cleaned_data['telefone']
        if not re.match("^\d{9}$", telefone):
            raise ValidationError("O número de telefone deve ter exatamente 9 dígitos.")
        if Perfil.objects.filter(telefone=telefone).exists():
            raise ValidationError("Este número de telefone já está registrado.")
        return telefone

    def clean_nome_empresa(self):
        nome_empresa = self.cleaned_data.get('nome_empresa')
        if not re.match("^[a-zA-Z0-9 ,\-]+$", nome_empresa):
            raise ValidationError("O nome da empresa deve conter apenas letras, números, espaços, vírgulas e hífens.")
        return nome_empresa

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("O campo usuário é obrigatório.")
        if re.match("^([a-zA-Z])\\1+$", username):
            raise ValidationError("O usuário não pode conter apenas caracteres repetidos.")
        return username
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("O campo sobrenome é obrigatório.")
        if re.match("^([a-zA-Z])\\1+$", last_name):
            raise ValidationError("O sobrenome não pode conter apenas caracteres repetidos.")
        return last_name

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError("O campo nome é obrigatório.")
        if re.match("^([a-zA-Z])\\1+$", nome):
            raise ValidationError("O nome não pode conter apenas caracteres repetidos.")
        return nome
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']  # Atualizando o email do usuário
        if commit:
            user.save()
            perfil = Perfil.objects.create(
                user=user,
                sobrenome=self.cleaned_data['last_name'],  # Salvando o sobrenome no perfil
                primeiro_nome=self.cleaned_data['username'],
                nome_empresa=self.cleaned_data['nome_empresa'],
                email_pessoal=self.cleaned_data['email'],  # Salvando o email pessoal no perfil
                email_empresa=self.cleaned_data['email_empresa'],
                telefone=self.cleaned_data['telefone']
            )
            # Envio de email de notificação
            html_content = render_to_string('usuarios/email_notification.html', {'perfil': perfil, 'user': user})
            text_content = strip_tags(html_content)  # Converta o HTML para texto simples para versão de texto do email
            email = EmailMultiAlternatives(
                'Novo formulário submetido',
                text_content,
                'suporteaoa.simulador@gmail.com',
                ['aurionascimento142@gmail.com', 'aurio2004@hotmail.com']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
        return user