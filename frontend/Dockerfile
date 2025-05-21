FROM node:20-alpine

WORKDIR /app

# Instalar dependências
COPY package.json package-lock.json* ./
RUN npm ci

# Copiar o código-fonte
COPY . .

# Expor a porta que o Next.js vai usar
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "run", "dev"]
