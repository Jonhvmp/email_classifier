"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { ptBR } from "date-fns/locale";
import { formatCategory, extractNameFromEmail } from "@/lib/utils";
import { API_URLS } from "@/lib/api-helpers";
import {
  ArrowLeft,
  Mail,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Copy,
  User,
  Calendar,
  MessageSquare,
  Reply
} from "lucide-react";

interface Email {
  id: number;
  subject: string;
  content: string;
  sender: string;
  category: string;
  suggested_response: string;
  created_at: string;
  confidence_score: number;
}

interface EmailDetailProps {
  id: number;
}

export function EmailDetail({ id }: EmailDetailProps) {
  const router = useRouter();
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [activeTab, setActiveTab] = useState("content");

  const fetchEmailDetails = useCallback(async () => {
    try {
      const emailId = id.toString();
      const apiUrl = API_URLS.EMAIL_DETAIL(emailId);
      console.log(`Buscando detalhes do email ${emailId} em: ${apiUrl}`);

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        cache: 'no-cache',
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Erro HTTP ${response.status}:`, errorText);

        if (response.status === 404) {
          throw new Error("Email não encontrado ou você não tem permissão para visualizá-lo");
        }

        if (errorText.includes("has no column named")) {
          console.error("Database schema error:", errorText);
          throw new Error("Erro de esquema do banco de dados. Execute as migrações do backend.");
        } else {
          try {
            const errorData = JSON.parse(errorText);
            throw new Error(errorData.error || errorData.message || "Falha ao buscar detalhes do email");
          } catch {
            throw new Error(`Falha ao buscar detalhes do email: ${response.status}`);
          }
        }
      }

      const data = await response.json();
      console.log("Email carregado com sucesso:", data);

      // Verificar se o email ainda está pendente
      if (data.category === 'pending' && retryCount < 20) {
        setIsPending(true);
        setRetryCount(prev => prev + 1);
        // Agendar nova verificação em 2 segundos
        setTimeout(fetchEmailDetails, 2000);
      } else {
        setIsPending(false);
        // Resetar contador quando processamento completo
        if (data.category !== 'pending') {
          setRetryCount(0);
        }
      }

      setEmail(data);
      setError(null);
    } catch (error) {
      console.error("Erro ao carregar detalhes do email:", error);
      setError(error instanceof Error ? error.message : "Erro desconhecido");
      setIsPending(false);
      toast.error("Erro ao carregar detalhes", {
        description: error instanceof Error ? error.message : "Não foi possível obter os detalhes deste email do servidor.",
      });
    } finally {
      setLoading(false);
    }
  }, [id, retryCount]);

  useEffect(() => {
    fetchEmailDetails();
  }, [fetchEmailDetails]);

  const handleCopyResponse = async () => {
    if (email?.suggested_response) {
      try {
        await navigator.clipboard.writeText(email.suggested_response);
        toast.success("Resposta copiada!", {
          description: "A resposta sugerida foi copiada para a área de transferência.",
        });
      } catch {
        toast.error("Erro ao copiar", {
          description: "Não foi possível copiar a resposta para a área de transferência.",
        });
      }
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    setRetryCount(0);
    fetchEmailDetails();
  };

  if (loading && !email) {
    return (
      <div className="container mx-auto px-4 py-4 sm:py-8">
        <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
          <div className="flex items-center gap-2 sm:gap-4 flex-wrap">
            <Skeleton className="h-8 w-8 sm:h-10 sm:w-10" />
            <Skeleton className="h-6 sm:h-8 w-32 sm:w-48" />
          </div>

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-full sm:w-3/4" />
              <Skeleton className="h-4 w-full sm:w-1/2" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full sm:w-3/4" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error && !email) {
    return (
      <div className="container mx-auto px-4 py-4 sm:py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 sm:gap-4 mb-4 sm:mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar
            </Button>
          </div>

          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (!email) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8">
      <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2 sm:gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Voltar</span>
            </Button>
            <h1 className="text-xl sm:text-2xl font-bold">Detalhes do Email</h1>
          </div>

          <div className="flex items-center gap-2">
            {isPending && (
              <Badge variant="secondary" className="animate-pulse">
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                <span className="hidden sm:inline">Processando...</span>
                <span className="sm:hidden">Proc...</span>
              </Badge>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''} ${!loading && 'mr-2'}`} />
              <span className="hidden sm:inline">Atualizar</span>
            </Button>
          </div>
        </div>

        {/* Email Details */}
        <Card>
          <CardHeader className="pb-2 sm:pb-4">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-1 sm:space-y-2 mb-2 sm:mb-0 flex-1">
                <CardTitle className="text-lg sm:text-xl leading-tight line-clamp-2">
                  {email.subject || "Sem assunto"}
                </CardTitle>
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 text-xs sm:text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {extractNameFromEmail(email.sender)}
                  </div>
                  <div className="hidden sm:flex items-center gap-1">
                    <Mail className="h-3 w-3" />
                    {email.sender}
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDistanceToNow(new Date(email.created_at), {
                      locale: ptBR,
                      addSuffix: true,
                    })}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant={email.category === "productive" ? "default" : "secondary"}
                  className="text-xs h-6"
                >
                  {email.category === "productive" ? (
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                  ) : (
                    <TrendingUp className="w-3 h-3 mr-1" />
                  )}
                  {formatCategory(email.category)}
                </Badge>
                <span className="text-xs text-muted-foreground font-mono">
                  {Math.round(email.confidence_score)}%
                </span>
              </div>
            </div>
          </CardHeader>

          {/* Use tabs for content and response */}
          <CardContent className="pt-2">
            {email.category === 'pending' ? (
              <Alert>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <AlertDescription>
                  Este email ainda está sendo processado pela nossa IA.
                  <span className="hidden sm:inline"> A página será atualizada automaticamente quando o processamento for concluído.</span>
                  {retryCount > 0 && ` (${retryCount}/20)`}
                </AlertDescription>
              </Alert>
            ) : (
              <Tabs
                defaultValue="content"
                value={activeTab}
                onValueChange={setActiveTab}
                className="w-full"
              >
                <TabsList className="grid grid-cols-2 mb-4">
                  <TabsTrigger value="content" className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    <span>Conteúdo</span>
                  </TabsTrigger>
                  <TabsTrigger
                    value="response"
                    className="flex items-center gap-1"
                    disabled={!email.suggested_response}
                  >
                    <Reply className="h-4 w-4" />
                    <span>Resposta Sugerida</span>
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="content" className="mt-0">
                  <div className="whitespace-pre-wrap text-sm bg-muted/50 p-3 sm:p-4 rounded-md overflow-x-auto">
                    {email.content}
                  </div>
                </TabsContent>

                <TabsContent value="response" className="mt-0">
                  <div className="flex justify-end mb-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopyResponse}
                      className="flex items-center gap-2"
                    >
                      <Copy className="h-4 w-4" />
                      Copiar
                    </Button>
                  </div>
                  <div className="whitespace-pre-wrap text-sm bg-blue-50 dark:bg-blue-950/20 p-3 sm:p-4 rounded-md border-l-4 border-blue-500 overflow-x-auto">
                    {email.suggested_response}
                  </div>
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
