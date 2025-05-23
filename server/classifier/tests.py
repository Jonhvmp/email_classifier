from django.test import TestCase, Client
from django.urls import reverse
from .models import Email
from unittest.mock import patch
from .ai_service import classify_email, suggest_response


class EmailModelTests(TestCase):
    def test_email_creation(self):
        """Teste de criação de um email"""
        email = Email.objects.create(
            subject="Teste de assunto",
            content="Conteúdo de teste",
            sender="test@example.com",
            category="productive",
            suggested_response="Resposta de teste"
        )
        self.assertEqual(email.subject, "Teste de assunto")
        self.assertEqual(email.category, "productive")
        self.assertEqual(str(email), "Teste de assunto - productive")


class EmailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = Email.objects.create(
            subject="Email de teste",
            content="Este é um email de teste",
            sender="test@example.com",
            category="productive",
            suggested_response="Resposta de teste"
        )

    def test_home_view(self):
        """Teste da view da página inicial"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'classifier/home.html')

    def test_email_list_view(self):
        """Teste da view de listagem de emails"""
        response = self.client.get(reverse('email_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'classifier/email_list.html')
        self.assertContains(response, "Email de teste")

    def test_email_detail_view(self):
        """Teste da view de detalhes de um email"""
        response = self.client.get(reverse('email_detail', args=[self.email.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'classifier/email_detail.html')
        self.assertContains(response, "Email de teste")
        self.assertContains(response, "test@example.com")


class AIServiceTests(TestCase):
    @patch('classifier.ai_service.co.classify')
    def test_classify_email(self, mock_classify):
        """Teste da função de classificação de emails"""
        # Configurando o mock para retornar uma classificação
        mock_response = type('obj', (object,), {
            'classifications': [type('obj', (object,), {'prediction': 'productive'})]
        })
        mock_classify.return_value = mock_response

        result = classify_email("Assunto de teste", "Conteúdo de teste")
        self.assertEqual(result, "productive")
        mock_classify.assert_called_once()

    @patch('classifier.ai_service.co.generate')
    def test_suggest_response(self, mock_generate):
        """Teste da função de sugestão de respostas"""
        # Configurando o mock para retornar uma resposta
        mock_response = type('obj', (object,), {
            'generations': [type('obj', (object,), {'text': 'Resposta sugerida de teste.'})]
        })
        mock_generate.return_value = mock_response

        result = suggest_response("Assunto de teste", "Conteúdo de teste", "productive")
        self.assertEqual(result, "Resposta sugerida de teste.")
        mock_generate.assert_called_once()
