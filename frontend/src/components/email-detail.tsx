"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
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
  Reply,
  Shield,
  Clock
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
  // const [activeTab, setActiveTab] = useState("content");

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
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          <div className="max-w-5xl mx-auto space-y-6">
            {/* Header Skeleton */}
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-center gap-3">
                <Skeleton className="h-9 w-9" />
                <Skeleton className="h-7 w-48" />
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-9 w-24" />
                <Skeleton className="h-9 w-28" />
              </div>
            </div>

            {/* Content Skeleton */}
            <Card className="shadow-sm">
              <CardHeader className="space-y-4">
                <div className="space-y-3">
                  <Skeleton className="h-6 w-full max-w-2xl" />
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-6">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-4 w-28" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-4 w-12" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-10 w-full max-w-xs" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (error && !email) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          <div className="max-w-5xl mx-auto">
            <div className="mb-6">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="gap-2 hover:bg-muted/80"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
            </div>

            <Alert variant="destructive" className="shadow-sm">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-sm leading-relaxed">
                {error}
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    );
  }

  if (!email) {
    return null;
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "productive":
        return <CheckCircle2 className="w-3 h-3" />;
      case "pending":
        return <RefreshCw className="w-3 h-3 animate-spin" />;
      default:
        return <TrendingUp className="w-3 h-3" />;
    }
  };

  const getCategoryVariant = (category: string) => {
    switch (category) {
      case "productive":
        return "default";
      case "pending":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="gap-2 hover:bg-muted/80 shrink-0"
              >
                <ArrowLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Voltar</span>
              </Button>
              <div>
                <h1 className="text-xl lg:text-2xl font-semibold tracking-tight">
                  Detalhes do Email
                </h1>
                <p className="text-sm text-muted-foreground mt-0.5">
                  ID #{id}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isPending && (
                <Badge variant="secondary" className="animate-pulse gap-1.5">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span className="text-xs">Processando...</span>
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={loading}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Atualizar</span>
              </Button>
            </div>
          </header>

          {/* Main Content */}
          <main>
            <Card className="shadow-sm border-border/50">
              <CardHeader className="pb-4">
                {/* Email Subject and Meta */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <CardTitle className="text-lg lg:text-xl leading-tight break-words">
                      {email.subject || "Sem assunto"}
                    </CardTitle>

                    {/* Email Metadata */}
                    <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 shrink-0" />
                        <span className="truncate font-medium">
                          {extractNameFromEmail(email.sender)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 shrink-0" />
                        <span className="truncate">
                          {email.sender}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 sm:col-span-2 lg:col-span-1">
                        <Calendar className="h-4 w-4 shrink-0" />
                        <span>
                          {formatDistanceToNow(new Date(email.created_at), {
                            locale: ptBR,
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Category and Confidence */}
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">
                          Categoria:
                        </span>
                        <Badge
                          variant={getCategoryVariant(email.category)}
                          className="gap-1.5"
                        >
                          {getCategoryIcon(email.category)}
                          {formatCategory(email.category)}
                        </Badge>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          Confiança:
                        </span>
                        <span className="text-sm font-mono font-medium">
                          {Math.round(email.confidence_score)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="pt-2">
                {email.category === 'pending' ? (
                  <Alert className="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/50">
                    <Clock className="h-4 w-4 text-amber-600" />
                    <AlertDescription className="text-amber-800 dark:text-amber-200">
                      <div className="space-y-1">
                        <p className="font-medium">Este email está sendo processado pela nossa IA.</p>
                        <p className="text-sm">
                          A página será atualizada automaticamente quando o processamento for concluído.
                          {retryCount > 0 && ` (${retryCount}/20)`}
                        </p>
                      </div>
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Tabs defaultValue="content" className="w-full">
                    <TabsList className="grid grid-cols-2 h-auto p-1">
                      <TabsTrigger value="content" className="gap-2 py-2.5">
                        <MessageSquare className="h-4 w-4" />
                        <span>Conteúdo</span>
                      </TabsTrigger>
                      <TabsTrigger
                        value="response"
                        className="gap-2 py-2.5"
                        disabled={!email.suggested_response}
                      >
                        <Reply className="h-4 w-4" />
                        <span>Resposta Sugerida</span>
                      </TabsTrigger>
                    </TabsList>

                    <div className="mt-6">
                      <TabsContent value="content" className="mt-0">
                        <div className="relative">
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <div className="whitespace-pre-wrap bg-muted/40 p-4 lg:p-6 rounded-lg border text-sm leading-relaxed overflow-x-auto">
                              {email.content}
                            </div>
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="response" className="mt-0">
                        <div className="space-y-4">
                          <div className="flex justify-between items-center">
                            <h3 className="text-sm font-medium text-muted-foreground">
                              Resposta sugerida pela IA
                            </h3>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={handleCopyResponse}
                              className="gap-2"
                            >
                              <Copy className="h-4 w-4" />
                              Copiar
                            </Button>
                          </div>

                          <div className="relative">
                            <div className="prose prose-sm max-w-none dark:prose-invert">
                              <div className="whitespace-pre-wrap bg-blue-50 dark:bg-blue-950/20 p-4 lg:p-6 rounded-lg border border-blue-200 dark:border-blue-800 text-sm leading-relaxed overflow-x-auto">
                                {email.suggested_response}
                              </div>
                            </div>
                          </div>
                        </div>
                      </TabsContent>
                    </div>
                  </Tabs>
                )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
