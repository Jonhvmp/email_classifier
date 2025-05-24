"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { ptBR } from "date-fns/locale";
import { formatCategory, smartTruncate, extractNameFromEmail } from "@/lib/utils";
import { API_URLS } from "@/lib/api-helpers";
import { Mail, Clock, TrendingUp, ArrowRight, CheckCircle2, AlertTriangle, Search } from "lucide-react";

interface Email {
  id: number;
  subject: string;
  sender: string;
  category: string;
  created_at: string;
  confidence_score: number;
  content?: string;
}

interface EmailListProps {
  searchTerm?: string;
  selectedCategories?: string[];
  currentPage?: number;
  emailsPerPage?: number;
  onTotalEmailsChange?: (total: number) => void;
  onEmailsLoaded?: (emails: Email[]) => void;
  emails?: Email[];
}

export default function EmailList({
  searchTerm = "",
  selectedCategories = [],
  currentPage = 1,
  emailsPerPage = 10,
  onTotalEmailsChange,
  onEmailsLoaded,
  emails: externalEmails = []
}: EmailListProps) {
  const [internalEmails, setInternalEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const emails = externalEmails.length > 0 ? externalEmails : internalEmails;

  const fetchEmails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log(`Buscando emails em: ${API_URLS.EMAILS_LIST}`);

      const response = await fetch(API_URLS.EMAILS_LIST, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const data = await response.json();
      console.log(`Resposta da API:`, data);

      // Verificar se a resposta tem a estrutura esperada
      if (!data.success) {
        throw new Error(data.error || 'Erro na resposta da API');
      }

      const emailsArray = data.emails || [];
      console.log(`${emailsArray.length} emails recebidos do servidor`);

      setInternalEmails(emailsArray);

      // Notificar o componente pai sobre os emails carregados
      if (onEmailsLoaded) {
        onEmailsLoaded(emailsArray);
      }

    } catch (error) {
      console.error("Erro ao carregar emails:", error);
      setError(error instanceof Error ? error.message : 'Erro desconhecido');
      toast.error("Erro ao carregar a lista de emails", {
        description: "Não foi possível obter a lista de emails do servidor.",
      });
      setInternalEmails([]); // Garantir que emails seja um array vazio em caso de erro
    } finally {
      setLoading(false);
    }
  }, [onEmailsLoaded]);

  useEffect(() => {
    // Só fazer fetch se não temos emails externos
    if (externalEmails.length === 0) {
      fetchEmails();
    } else {
      // Se temos emails externos, não precisamos carregar
      setLoading(false);
    }
  }, [externalEmails.length, fetchEmails]);

  // Filtrar emails baseado na busca e categorias selecionadas
  const filteredEmails = useMemo(() => {
    const filtered = emails.filter(email => {
      // Filtro de busca por assunto ou remetente
      const matchesSearch = searchTerm === "" ||
        email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.sender.toLowerCase().includes(searchTerm.toLowerCase());

      // Filtro por categoria
      const matchesCategory = selectedCategories.length === 0 ||
        selectedCategories.includes(email.category);

      return matchesSearch && matchesCategory;
    });

    // Notificar o total de emails filtrados
    if (onTotalEmailsChange) {
      onTotalEmailsChange(filtered.length);
    }

    return filtered;
  }, [emails, searchTerm, selectedCategories, onTotalEmailsChange]);

  // Calcular emails para a página atual
  const paginatedEmails = useMemo(() => {
    const startIndex = (currentPage - 1) * emailsPerPage;
    const endIndex = startIndex + emailsPerPage;
    return filteredEmails.slice(startIndex, endIndex);
  }, [filteredEmails, currentPage, emailsPerPage]);

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(5)].map((_, index) => (
          <Card key={index} className="border-slate-200 dark:border-slate-700">
            <CardHeader className="pb-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <Skeleton className="h-4 w-20" />
              </div>
              <div className="mt-4">
                <Skeleton className="h-2 w-full" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <div className="mx-auto w-24 h-24 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-6">
          <AlertTriangle className="h-12 w-12 text-red-500" />
        </div>
        <h3 className="text-xl font-semibold mb-2">Erro ao carregar emails</h3>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          {error}
        </p>
        <Button onClick={() => window.location.reload()} className="gap-2">
          <ArrowRight className="h-4 w-4" />
          Tentar novamente
        </Button>
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="mx-auto w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
          <Mail className="h-12 w-12 text-slate-400" />
        </div>
        <h3 className="text-xl font-semibold mb-2">Nenhum email classificado</h3>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          Ainda não há emails processados. Submeta um email para começar a ver os resultados aqui.
        </p>
        <Link href="/">
          <Button className="gap-2">
            <ArrowRight className="h-4 w-4" />
            Classificar primeiro email
          </Button>
        </Link>
      </div>
    );
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "productive":
        return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400";
      case "promotional":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
      case "social":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
      default:
        return "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400";
    }
  };

  const getConfidenceIcon = (score: number) => {
    if (score >= 80) return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
    if (score >= 60) return <TrendingUp className="h-4 w-4 text-yellow-500" />;
    return <AlertTriangle className="h-4 w-4 text-red-500" />;
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 80) return "Alta confiança";
    if (score >= 60) return "Média confiança";
    return "Baixa confiança";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground font-medium">
          <Mail className="h-4 w-4" />
          <span>
            {filteredEmails.length === emails.length
              ? `${emails.length} emails`
              : `${filteredEmails.length} de ${emails.length} emails (filtrados)`
            }
          </span>
        </div>
        {filteredEmails.length > emailsPerPage && (
          <div className="text-sm text-muted-foreground font-medium">
            Mostrando {Math.min(emailsPerPage, filteredEmails.length - (currentPage - 1) * emailsPerPage)} de {filteredEmails.length}
          </div>
        )}
      </div>

      {filteredEmails.length === 0 && emails.length > 0 && (
        <div className="text-center py-16">
          <div className="mx-auto w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
            <Search className="h-12 w-12 text-slate-400" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Nenhum email encontrado</h3>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto">
            Nenhum email corresponde aos filtros aplicados. Tente ajustar os critérios de busca.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {paginatedEmails.map((email) => (
          <Link href={`/emails/${email.id}`} key={email.id} className="block">
            <Card className="group hover:shadow-md transition-all duration-200 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="card-title text-lg group-hover:text-primary transition-colors">
                      {smartTruncate(email.subject, 80)}
                    </CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-muted-foreground font-medium">De:</span>
                      <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 truncate">
                        {smartTruncate(extractNameFromEmail(email.sender) || email.sender, 40)}
                      </span>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-primary group-hover:translate-x-1 transition-all duration-200 flex-shrink-0 ml-4" />
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Badge className={`${getCategoryColor(email.category)} border-0 font-semibold`}>
                      {formatCategory(email.category)}
                    </Badge>
                    <div className="flex items-center gap-1">
                      {getConfidenceIcon(email.confidence_score)}
                      <span className="text-xs text-muted-foreground font-medium">
                        {getConfidenceLabel(email.confidence_score)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground font-medium">
                    <Clock className="h-3 w-3" />
                    <span>
                      {formatDistanceToNow(new Date(email.created_at), { addSuffix: true, locale: ptBR })}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground font-medium">Pontuação de confiança</span>
                    <span className="font-bold">{Math.round(email.confidence_score)}%</span>
                  </div>
                  <Progress
                    value={email.confidence_score}
                    className="h-2"
                  />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {paginatedEmails.length === 0 && filteredEmails.length === 0 && emails.length === 0 && (
        <div className="text-center py-16">
          <div className="mx-auto w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
            <Mail className="h-12 w-12 text-slate-400" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Nenhum email classificado</h3>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto">
            Ainda não há emails processados. Submeta um email para começar a ver os resultados aqui.
          </p>
          <Link href="/">
            <Button className="gap-2">
              <ArrowRight className="h-4 w-4" />
              Classificar primeiro email
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
}

export function EmailListFallback() {
  return (
    <div className="space-y-6">
      {[...Array(5)].map((_, index) => (
        <Card key={index} className="border-slate-200 dark:border-slate-700">
          <CardHeader className="pb-4">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Skeleton className="h-6 w-24" />
                <Skeleton className="h-4 w-32" />
              </div>
              <Skeleton className="h-4 w-20" />
            </div>
            <div className="mt-4">
              <Skeleton className="h-2 w-full" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
