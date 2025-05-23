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
