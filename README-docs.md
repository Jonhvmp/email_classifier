# Documentação do Email Classifier System

Este diretório contém a documentação completa do sistema Email Classifier, criada com MkDocs Material.

## 📚 Conteúdo da Documentação

### 🏠 Página Inicial
- **index.md**: Visão geral do sistema e introdução

### 🏗️ Arquitetura
- **overview.md**: Visão geral da arquitetura do sistema
- **models.md**: Documentação dos modelos de dados
- **apis.md**: Documentação completa das APIs e endpoints

### ⚡ Funcionalidades
- **classification.md**: Sistema de classificação de emails com IA
- **job-queue.md**: Sistema de filas para processamento assíncrono
- **rate-limiting.md**: Controle de uso das APIs externas
- **file-upload.md**: Sistema de upload e processamento de arquivos

### ⚙️ Configuração
- **environment.md**: Variáveis de ambiente e configuração
- **installation.md**: Guia completo de instalação
- **deployment.md**: Guia de deployment para produção

## 🚀 Como Usar a Documentação

### Visualizar Localmente

1. **Instalar dependências**:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Iniciar servidor de desenvolvimento**:
   ```bash
   # Na raiz do projeto (onde está mkdocs.yml)
   mkdocs serve
   ```

3. **Acessar no navegador**:
   ```
   http://127.0.0.1:8000
   ```

### Deploy no GitHub Pages

```bash
# Deploy automático
mkdocs gh-deploy
```

A documentação ficará disponível em: `https://jonhvmp.github.io/email_classifier`

## 🛠️ Ferramentas Utilizadas

- **[MkDocs](https://www.mkdocs.org/)**: Gerador de sites estáticos
- **[Material Theme](https://squidfunk.github.io/mkdocs-material/)**: Tema moderno e responsivo
- **[Awesome Pages Plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)**: Navegação aprimorada

## 📝 Como Contribuir

### Editando Documentação

1. **Editar arquivos Markdown** na pasta `docs/`
2. **Testar localmente** com `mkdocs serve`
3. **Fazer commit** das mudanças
4. **Deploy** com `mkdocs gh-deploy`

### Adicionando Novas Páginas

1. **Criar arquivo .md** na pasta apropriada em `docs/`
2. **Adicionar à navegação** no `mkdocs.yml`:
   ```yaml
   nav:
     - Nova Seção:
       - Nova Página: caminho/para/arquivo.md
   ```

### Estrutura Recomendada

```markdown
# Título da Página

## Seção Principal

### Subseção

Conteúdo da documentação...

#### Códigos
```python
# Exemplo de código
def exemplo():
    return "Hello World"
```

#### Tabelas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id    | int  | Identificador |

#### Alertas
!!! warning "Atenção"
    Informação importante

!!! tip "Dica"
    Sugestão útil
```

## 🎨 Personalização

### Tema Material

O tema está configurado com:
- **Paleta**: Azul com modo claro/escuro
- **Navegação**: Tabs, seções e busca
- **Código**: Syntax highlighting e botão de copiar
- **Extensões**: Markdown avançado com tabelas, alertas, etc.

### Extensões Ativas

- `codehilite`: Highlight de código
- `admonition`: Caixas de alerta/aviso
- `toc`: Índice automático com permalinks
- `pymdownx.*`: Extensões avançadas do Python Markdown

## 📋 Comandos Úteis

```bash
# Verificar configuração
mkdocs config

# Build para produção
mkdocs build --clean

# Servir com porta específica
mkdocs serve --dev-addr=127.0.0.1:8080

# Build estrito (falha em warnings)
mkdocs build --strict

# Deploy forçado
mkdocs gh-deploy --force
```

## 🔗 Links Úteis

- [Documentação do MkDocs](https://www.mkdocs.org/)
- [Material Theme Docs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages](https://pages.github.com/)

## 📄 Licença

Esta documentação segue a mesma licença do projeto principal.
