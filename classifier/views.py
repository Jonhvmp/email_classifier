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
    View da página inicial com formulário para submissão de email.
    """
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.save(commit=False)

            input_method = form.cleaned_data.get('input_method')

            # Processar entrada baseada no método escolhido
            if input_method == 'file' and email.file:
                # Salvar o arquivo temporariamente
                file_path = os.path.join(settings.MEDIA_ROOT, email.file.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb+') as destination:
                    for chunk in email.file.chunks():
                        destination.write(chunk)

                # Extrair texto do arquivo
                try:
                    subject, content = extract_text_from_file(file_path)
                    email.subject = subject if email.subject == '' else email.subject
                    email.content = content
                except Exception as e:
                    messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
                    return render(request, 'classifier/home.html', {'form': form})

            # Limpar o texto para processamento
            clean_content = clean_text(email.content)            # Classificar o email
            try:
                category = classify_email(email.subject, clean_content)
                email.category = category

                # Sugerir resposta
                email.suggested_response = suggest_response(email.subject, clean_content, category)
            except Exception as e:
                messages.error(request, f'Erro ao processar o email: {str(e)}')
                return render(request, 'classifier/home.html', {'form': form})

            email.save()
            messages.success(request, 'Email classificado com sucesso!')
            return redirect('email_detail', pk=email.pk)
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
    View para mostrar os detalhes de um email específico.
    """
    model = Email
    template_name = 'classifier/email_detail.html'
    context_object_name = 'email'

def about(request):
    """
    View da página sobre o projeto.
    """
    return render(request, 'classifier/about.html')
