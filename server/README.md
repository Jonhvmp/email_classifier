# Email Classifier

Este é um projeto para classificação de emails e geração de respostas automáticas usando inteligência artificial (Cohere API).

## Requisitos

- Python 3.13.3 ou superior
- Django 4.2.7
- Cohere API
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
5. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   SECRET_KEY=sua-chave-secreta-aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   COHERE_API_KEY=sua-chave-api-cohere-aqui
   ```
6. Execute as migrações:
   ```
   python manage.py migrate
   ```
7. Inicie o servidor:
   ```
   python manage.py runserver
   ```

## Funcionalidades

- Classificação de emails em duas categorias: Produtivo e Improdutivo
- Geração de respostas automáticas personalizadas para cada categoria
- Interface web intuitiva para submissão e visualização dos resultados
- Armazenamento de histórico de emails classificados

## Estrutura do Projeto

```
email_classifier/
│
├── classifier/                # Aplicação principal
│   ├── migrations/           # Migrações do banco de dados
│   ├── templates/            # Templates HTML específicos da aplicação
│   ├── __init__.py
│   ├── admin.py              # Configuração do admin do Django
│   ├── ai_service.py         # Serviço de integração com a Cohere API
│   ├── apps.py
│   ├── forms.py              # Formulários da aplicação
│   ├── models.py             # Modelos de dados
│   ├── tests.py              # Testes automatizados
│   ├── urls.py               # URLs da aplicação
│   └── views.py              # Views da aplicação
│
├── email_classifier/         # Projeto Django principal
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Configurações do projeto
│   ├── urls.py               # URLs do projeto
│   └── wsgi.py
│
├── templates/                # Templates HTML gerais
│   └── base.html             # Template base
│
├── static/                   # Arquivos estáticos (CSS, JS, imagens)
│
├── .env                      # Variáveis de ambiente (não versionado)
├── .gitignore                # Arquivos ignorados pelo git
├── manage.py                 # Script de gerenciamento do Django
├── README.md                 # Documentação do projeto
└── requirements.txt          # Dependências do projeto
```

## Uso

1. Acesse a página inicial
2. Preencha o formulário com os dados do email
3. Clique em "Classificar"
4. Visualize a classificação e a resposta sugerida

## Teste

Para executar os testes:

```
python manage.py test
```

ou

```
pytest
```
