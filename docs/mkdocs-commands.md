# Comandos MkDocs

## Instalação e Configuração

### Instalar MkDocs
```bash
cd server
pip install -r requirements.txt
```

### Verificar Instalação
```bash
mkdocs --version
```

## Desenvolvimento da Documentação

### Iniciar Servidor de Desenvolvimento
```bash
# Na raiz do projeto (onde está mkdocs.yml)
mkdocs serve

# Servidor rodará em http://127.0.0.1:8000
```

### Opções do Servidor
```bash
# Porta específica
mkdocs serve --dev-addr=127.0.0.1:8080

# Modo verboso
mkdocs serve --verbose

# Hot reload automático
mkdocs serve --livereload
```

## Build e Deploy

### Gerar Site Estático
```bash
mkdocs build
```

### Build com Limpeza
```bash
mkdocs build --clean
```

### Deploy no GitHub Pages
```bash
mkdocs gh-deploy
```

### Deploy com Branch Específica
```bash
mkdocs gh-deploy --remote-branch=gh-pages
```

## Estrutura de Arquivos

### Estrutura Recomendada
```
projeto/
├── mkdocs.yml              # Configuração principal
├── docs/                   # Documentos fonte
│   ├── index.md           # Página inicial
│   ├── architecture/      # Arquitetura
│   │   ├── overview.md
│   │   ├── models.md
│   │   └── apis.md
│   ├── features/          # Funcionalidades
│   │   ├── classification.md
│   │   ├── job-queue.md
│   │   ├── rate-limiting.md
│   │   └── file-upload.md
│   └── setup/            # Configuração
│       ├── environment.md
│       ├── installation.md
│       └── deployment.md
└── site/                 # Site gerado (não versionado)
```

## Validação e Testes

### Verificar Links
```bash
# Plugin para verificar links quebrados
pip install mkdocs-linkcheck

# Adicionar ao mkdocs.yml:
# plugins:
#   - linkcheck
```

### Validar Configuração
```bash
mkdocs config
```

### Build de Teste
```bash
mkdocs build --strict
```

## Personalização

### Adicionar Plugins
```yaml
# mkdocs.yml
plugins:
  - search
  - awesome-pages
  - macros
```

### Temas Populares
```yaml
# Material Theme
theme:
  name: material

# ReadTheDocs Theme
theme:
  name: readthedocs

# Bootswatch Themes
theme:
  name: bootstrap
  bootstrap_version: 4
```

### Extensões Markdown
```yaml
markdown_extensions:
  - codehilite
  - admonition
  - toc:
      permalink: true
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
```

## Automatização

### GitHub Actions para Deploy
```yaml
# .github/workflows/docs.yml
name: Deploy Documentation
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.x
    - run: pip install mkdocs-material
    - run: mkdocs gh-deploy --force
```

### Script de Deploy Local
```bash
#!/bin/bash
# deploy-docs.sh
echo "Building documentation..."
mkdocs build --clean

echo "Deploying to GitHub Pages..."
mkdocs gh-deploy

echo "Documentation deployed successfully!"
```

## Dicas de Uso

### Live Reload
- O servidor detecta mudanças automaticamente
- Recarrega a página no navegador
- Funciona para arquivos .md e mkdocs.yml

### Navegação
- Use `nav` no mkdocs.yml para estruturar
- Arquivos não listados aparecem alfabeticamente
- Suporte a subseções ilimitadas

### Links Internos
```markdown
# Links relativos funcionam
[Instalação](setup/installation.md)
[API Status](../api/status.md)

# Âncoras em páginas
[Seção específica](page.md#secao)
```

### Imagens e Assets
```markdown
# Pasta images/ dentro de docs/
![Diagrama](images/architecture.png)

# CSS e JS customizados
# Adicionar em mkdocs.yml:
# extra_css:
#   - css/custom.css
```

## Troubleshooting

### Problemas Comuns

#### Erro de Build
```bash
# Verificar sintaxe YAML
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"

# Build verboso
mkdocs build --verbose
```

#### Links Quebrados
```bash
# Verificar paths relativos
# Usar caminhos a partir da pasta docs/
```

#### Tema Não Carrega
```bash
# Verificar instalação do tema
pip list | grep mkdocs

# Reinstalar tema
pip install --upgrade mkdocs-material
```

#### GitHub Pages Não Atualiza
```bash
# Forçar deploy
mkdocs gh-deploy --force

# Verificar configuração do repositório
# Settings > Pages > Source: gh-pages branch
```
