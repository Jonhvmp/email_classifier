import pytest
from unittest.mock import patch, MagicMock
from classifier.ai_service import classify_email, suggest_response, process_email

@pytest.fixture
def mock_genai():
    with patch('classifier.ai_service.genai') as mock_genai:
        # Set up mock response for classification
        mock_response = MagicMock()
        mock_response.text = "productive|85.5"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        yield mock_genai

def test_classify_email(mock_genai):
    """Test email classification with Gemini."""
    # Call the function
    result = classify_email("Help with login", "I'm having trouble logging into my account")

    # Verify the result
    assert result == "productive"
    # Verify Gemini was called with appropriate parameters
    mock_genai.GenerativeModel.assert_called_once()
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.assert_called_once()

def test_suggest_response(mock_genai):
    """Test response suggestion with Gemini."""
    # Configure mock for response generation
    mock_model = mock_genai.GenerativeModel.return_value
    mock_response = MagicMock()
    mock_response.text = "Prezado(a),\n\nAgradecemos seu contato. Sua solicitação foi recebida e será analisada pela nossa equipe técnica.\n\nAtenciosamente,\nEquipe de Atendimento"
    mock_model.generate_content.return_value = mock_response

    # Call the function
    result = suggest_response("Help needed", "I need assistance with my account", "productive")

    # Verify the structure of the response
    assert "Prezado(a)" in result
    assert "Atenciosamente" in result
    assert len(result) > 30

def test_process_email():
    """Test the complete email processing flow."""
    with patch('classifier.ai_service.classify_email') as mock_classify:
        with patch('classifier.ai_service.suggest_response') as mock_suggest:
            # Set up mocks
            mock_classify.return_value = "productive"
            mock_suggest.return_value = "Mocked response"

            # Call the function
            email_data = {
                'subject': 'Test Subject',
                'content': 'Test Content',
                'sender': 'test@example.com'
            }
            result = process_email(email_data)

            # Verify the result structure
            assert 'category' in result
            assert 'confidence_score' in result
            assert 'suggested_response' in result
            assert result['category'] == "productive"
            assert result['suggested_response'] == "Mocked response"

def test_fallback_classification():
    """Test fallback classification when Gemini fails."""
    with patch('classifier.ai_service.genai.GenerativeModel') as mock_model_class:
        # Make the Gemini call fail
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        # Call the function with clearly productive content
        result = classify_email("Bug report", "System is crashing when I try to save")

        # Should fall back to heuristic classification
        assert result == "productive"
