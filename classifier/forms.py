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

    # Campos para controlar se deve usar os dados do arquivo ou inserir manualmente
    use_file_subject = forms.BooleanField(required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        label='Usar campo de assunto acima (ignorar assunto do arquivo)')

    use_file_sender = forms.BooleanField(required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        label='Usar campo de remetente acima (ignorar remetente do arquivo)')

    class Meta:
        model = Email
        fields = ['sender', 'subject', 'content', 'file']
        widgets = {
            'sender': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subject': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 6}),
            'file': forms.FileInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'accept': '.txt,.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sender'].required = False
        self.fields['subject'].required = False
        self.fields['content'].required = False

    def clean(self):
        print("Iniciando validação do formulário...")
        cleaned_data = super().clean()
        input_method = cleaned_data.get('input_method')
        content = cleaned_data.get('content')
        file = cleaned_data.get('file')
        print(f"Input method: {input_method}")
        print(f"Content present: {'Sim' if content else 'Não'}")
        print(f"File present: {'Sim' if file else 'Não'}")

        use_file_subject = cleaned_data.get('use_file_subject', False)
        use_file_sender = cleaned_data.get('use_file_sender', False)
        print(f"Usar campo de assunto: {use_file_subject}")
        print(f"Usar campo de remetente: {use_file_sender}")

        if input_method == 'text' and not content:
            self.add_error('content', 'Por favor, insira o conteúdo do email.')
        if input_method == 'file':
            if not file:
                print("Erro: Arquivo não fornecido no modo upload")
                self.add_error('file', 'Por favor, faça upload de um arquivo.')

            # Se marcou para usar o campo de assunto manual e não preencheu
            if use_file_subject and not cleaned_data.get('subject'):
                print("Erro: Campo de assunto vazio mas checkbox marcado")
                self.add_error('subject', 'Por favor, preencha o assunto ou desmarque a opção para definir manualmente.')

            # Se marcou para usar o campo de remetente manual e não preencheu
            if use_file_sender and not cleaned_data.get('sender'):
                print("Erro: Campo de remetente vazio mas checkbox marcado")
                self.add_error('sender', 'Por favor, preencha o remetente ou desmarque a opção para definir manualmente.')

            # Verificar a extensão do arquivo se ele existir
            if file:
                ext = os.path.splitext(file.name)[1].lower()
                if ext not in ['.txt', '.pdf']:
                    print(f"Erro: Tipo de arquivo inválido: {ext}")
                    self.add_error('file', 'Apenas arquivos .txt ou .pdf são permitidos.')
                else:
                    print(f"Tipo de arquivo aceito: {ext}")
                    # Salvar o tipo de arquivo
                    cleaned_data['file_type'] = ext[1:] 

        return cleaned_data
