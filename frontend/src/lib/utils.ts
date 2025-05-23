import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combina classes com clsx e tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formata uma categoria para exibição
 */
export function formatCategory(category: string): string {
  if (category === "productive") {
    return "Produtivo";
  } else if (category === "unproductive") {
    return "Improdutivo";
  }
  return category.charAt(0).toUpperCase() + category.slice(1);
}

/**
 * Tenta extrair um nome de um endereço de email
 */
export function extractNameFromEmail(email: string): string {
  if (!email) return "";

  // Tenta extrair o nome da parte antes do @
  const beforeAt = email.split('@')[0];
  if (!beforeAt) return email;

  // Substitui pontos e underscores por espaços
  const name = beforeAt
    .replace(/\./g, ' ')
    .replace(/_/g, ' ')
    .replace(/\d+/g, ''); // Remove números

  // Formata o nome (primeiras letras maiúsculas)
  return name
    .split(' ')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ')
    .trim();
}

/**
 * Trunca um texto para um comprimento máximo, adicionando "..." no final se necessário
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Trunca texto de forma inteligente, tentando quebrar em palavras
 */
export function smartTruncate(text: string, maxLength: number, suffix: string = '...'): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;

  // Se o texto for muito longo, tenta truncar na última palavra completa
  const truncated = text.substring(0, maxLength - suffix.length);
  const lastSpaceIndex = truncated.lastIndexOf(' ');

  // Se encontrou um espaço e não está muito próximo do início
  if (lastSpaceIndex > maxLength * 0.7) {
    return truncated.substring(0, lastSpaceIndex) + suffix;
  }

  // Caso contrário, trunca no limite exato
  return truncated + suffix;
}

/**
 * Trunca texto preservando quebras de linha para preview
 */
export function truncatePreview(text: string, maxLines: number = 3, maxCharsPerLine: number = 80): string {
  if (!text) return '';

  // Divide o texto em linhas
  const lines = text.split('\n');

  // Limita o número de linhas
  const limitedLines = lines.slice(0, maxLines);

  // Trunca cada linha se necessário
  const truncatedLines = limitedLines.map(line =>
    smartTruncate(line.trim(), maxCharsPerLine, '...')
  );

  // Se havia mais linhas, adiciona indicador
  if (lines.length > maxLines) {
    truncatedLines[truncatedLines.length - 1] += ' (...)';
  }

  return truncatedLines.join('\n');
}

/**
 * Quebra texto longo em múltiplas linhas para melhor legibilidade
 */
export function wrapText(text: string, maxLineLength: number = 100): string {
  if (!text) return '';

  const words = text.split(' ');
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    // Se adicionar a palavra ultrapassar o limite
    if (currentLine && (currentLine + ' ' + word).length > maxLineLength) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = currentLine ? currentLine + ' ' + word : word;
    }
  }

  // Adiciona a última linha se houver conteúdo
  if (currentLine) {
    lines.push(currentLine);
  }

  return lines.join('\n');
}

/**
 * Obtém um resumo do texto, mantendo as primeiras e últimas palavras se necessário
 */
export function summarizeText(text: string, maxLength: number = 150): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;

  const halfLength = Math.floor((maxLength - 5) / 2); // 5 para " ... "
  const start = text.substring(0, halfLength);
  const end = text.substring(text.length - halfLength);

  return start.trim() + ' ... ' + end.trim();
}

/**
 * Remove HTML tags e entidades, útil para text vindo de rich text
 */
export function stripHtml(html: string): string {
  if (!html) return '';

  // Remove tags HTML
  const withoutTags = html.replace(/<[^>]*>/g, '');

  // Decodifica entidades HTML comuns
  const entities: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#39;': "'",
    '&nbsp;': ' '
  };

  return withoutTags.replace(/&[a-zA-Z0-9#]+;/g, (entity) => {
    return entities[entity] || entity;
  });
}

/**
 * Formata texto para exibição em cards/listas
 */
export function formatTextForCard(text: string, options: {
  maxLength?: number;
  maxLines?: number;
  preserveLineBreaks?: boolean;
} = {}): string {
  const {
    maxLength = 200,
    maxLines = 2,
    preserveLineBreaks = false
  } = options;

  if (!text) return '';

  // Remove HTML se presente
  let cleanText = stripHtml(text);

  // Se não deve preservar quebras de linha, substitui por espaços
  if (!preserveLineBreaks) {
    cleanText = cleanText.replace(/\s+/g, ' ').trim();
  }

  // Se tem limite de linhas e deve preservar quebras
  if (preserveLineBreaks && maxLines) {
    cleanText = truncatePreview(cleanText, maxLines, maxLength / maxLines);
  }

  // Trunca pelo comprimento total
  return smartTruncate(cleanText, maxLength);
}
