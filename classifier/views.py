from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.conf import settings
import os
from .models import Email
from .forms import EmailForm
from .ai_service import classify_email, suggest_response
from .utils import extract_text_from_file, clean_text

def home(request):
    """
    View da p?gina inicial com formul?rio para submiss?o de email.
    """
    if request.method == 'POST':
        logging.debug('\n\n')
        logging.debug('='*50)
        logging.info('POST REQUEST RECEBIDO')
        logging.debug('='*50)
        logging.debug(f'POST data: {request.POST}')
        logging.debug(f'FILES data: {request.FILES}')

        form = EmailForm(request.POST, request.FILES)
        logging.debug(f'Form criado, ? v?lido? {form.is_valid()}')

        if form.is_valid():
            logging.info('Form is valid')
            email = form.save(commit=False)

            input_method = form.cleaned_data.get('input_method')
            logging.debug(f'Input method: {input_method}')

            if input_method == 'file' and email.file:
                # Salvar o arquivo temporariamente
                # Save the uploaded file using Django's storage system
                email.file.save(email.file.name, email.file, save=True)
                file_path = email.file.path  # Get the file path from the storage system
                # Extrair texto do arquivo
                try:
                    subject_from_file, content_from_file, sender_from_file = extract_text_from_file(file_path)

                    use_manual_subject = form.cleaned_data.get('use_file_subject', False)
                    if not use_manual_subject or not email.subject:
                        # Usar o assunto do arquivo (quando checkbox está desmarcado ou quando campo está vazio)
                        email.subject = subject_from_file

                    use_manual_sender = form.cleaned_data.get('use_file_sender', False)
                    if not use_manual_sender:
                        if sender_from_file:
                            email.sender = sender_from_file
                        else:
                            import re
                            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                            email_matches = re.findall(email_pattern, content_from_file)
                            if email_matches:
                                email.sender = email_matches[0]
                            else:
                                email.sender = 'noreply@example.com'
                    email.content = content_from_file
                except Exception as e:
                    messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
                    form = EmailForm()
                    return render(request, 'classifier/home.html', {'form': form})

            # Limpar o texto para processamento
            clean_content = clean_text(email.content)

            # Classificar o email
            try:
                print(f'Antes de classificar - Assunto: {email.subject}, Conte?do: {clean_content[:100]}...')
                category = classify_email(email.subject, clean_content)
                print(f'Categoria classificada: {category}')
                email.category = category
                try:
                    from .ai_service import classification_confidence
                    email.confidence_score = float(classification_confidence)
                    print(f'Nível de confiança: {classification_confidence}')
                except Exception as e:
                    email.confidence_score = 75.0
                    print(f'Erro ao obter nível de confiança: {e}')

                # Sugerir resposta
                print('Gerando resposta sugerida...')
                email.suggested_response = suggest_response(email.subject, clean_content, category)
                print(f'Resposta gerada: {email.suggested_response[:100]}...')
            except Exception as e:
                print(f'ERRO na classificação: {str(e)}')
                messages.error(request, f'Erro ao processar o email: {str(e)}')
                form = EmailForm()
                return render(request, 'classifier/home.html', {'form': form})

            try:
                print('Salvando email no banco de dados...')
                email.save()
                print(f'Email salvo com ID: {email.pk}')
                messages.success(request, 'Email classificado com sucesso!')
                print(f'Redirecionando para email_detail com pk={email.pk}')
                return redirect('email_detail', pk=email.pk)
            except Exception as e:
                print(f'ERRO ao salvar email: {str(e)}')
                messages.error(request, f'Erro ao salvar o email: {str(e)}')
                form = EmailForm()
                return render(request, 'classifier/home.html', {'form': form})
        else:
            print('Form is invalid')
            print(f'Form errors: {form.errors}')
    else:
        form = EmailForm()

    return render(request, 'classifier/home.html', {'form': form})

class EmailListView(ListView):
    """
    View para listar todos os emails classificados.
    """
    model = Email
    template_name = 'classifier/email_list.html'
    context_object_name = 'emails'
    paginate_by = 10

class EmailDetailView(DetailView):
    """
    View para mostrar os detalhes de um email espec?fico.
    """
    model = Email
    template_name = 'classifier/email_detail.html'
    context_object_name = 'email'

def about(request):
    """
    View da p?gina sobre o projeto.
    """
    return render(request, 'classifier/about.html')
