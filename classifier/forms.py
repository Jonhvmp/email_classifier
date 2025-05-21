from django import forms
from .models import Email
import os

class EmailForm(forms.ModelForm):
    """
    Formulário para submissão de emails para classificação.
    """

    # Campo para escolher entre entrada direta de texto ou upload de arquivo
    input_method = forms.ChoiceField(
        choices=[('text', 'Texto direto'), ('file', 'Upload de arquivo')],
        widget=forms.RadioSelect(attrs={'class': 'mr-2 text-blue-500'}),
        initial='text',
        required=True
    )

    class Meta:
        model = Email
        fields = ['sender', 'subject', 'content', 'file']
        widgets = {
            'sender': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subject': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 6}),
            'file': forms.FileInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': '.txt,.pdf'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        input_method = cleaned_data.get('input_method')
        content = cleaned_data.get('content')
        file = cleaned_data.get('file')

        if input_method == 'text' and not content:
            self.add_error('content', 'Por favor, insira o conteúdo do email.')

        if input_method == 'file':
            if not file:
                self.add_error('file', 'Por favor, faça upload de um arquivo.')
            else:
                # Verificar a extensão do arquivo
                ext = os.path.splitext(file.name)[1].lower()
                if ext not in ['.txt', '.pdf']:
                    self.add_error('file', 'Apenas arquivos .txt ou .pdf são permitidos.')
                else:
                    # Salvar o tipo de arquivo
                    cleaned_data['file_type'] = ext[1:]  # Remover o ponto

        return cleaned_data
