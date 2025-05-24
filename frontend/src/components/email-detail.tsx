"use client";

import { useState, useEffect, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Progress } from "@/components/ui/progress";
import { formatCategory } from "@/lib/utils";
import { AlertCircle, Loader2 } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { API_URLS } from "@/lib/api-helpers";

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

export function EmailDetail({ id }: { id: string }) {
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

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

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !email) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Email não encontrado</AlertTitle>
          <AlertDescription>
            {error || "O email solicitado não existe ou foi removido."}
          </AlertDescription>
        </Alert>

        <div className="text-center py-10">
          <h3 className="text-lg font-medium">Email não encontrado</h3>
          <p className="text-muted-foreground">
            O email solicitado não existe ou foi removido.
          </p>
        </div>
      </div>
    );
  }

  // Se o email ainda está pendente de processamento
  if (isPending) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold mb-2">{email.subject}</h2>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>De: {email.sender}</span>
            <span>•</span>
            <span>
              {format(new Date(email.created_at), "PPP 'às' HH:mm", { locale: ptBR })}
            </span>
          </div>
        </div>

        <Alert className="bg-blue-50 border-blue-200 text-blue-800">
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
          <AlertTitle>Processando email</AlertTitle>
          <AlertDescription>
            Este email ainda está sendo processado pela nossa IA.
            Aguarde alguns instantes e atualize a página para ver o resultado.
          </AlertDescription>
        </Alert>

        <Card>
          <CardContent className="p-4">
            <pre className="whitespace-pre-wrap font-sans">{email.content}</pre>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2 tracking-tight">{email.subject}</h2>
        <div className="flex items-center gap-4 text-sm text-muted-foreground font-medium">
          <span>De: {email.sender}</span>
          <span>•</span>
          <span>
            {format(new Date(email.created_at), "PPP 'às' HH:mm", { locale: ptBR })}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Badge
          variant={email.category === "productive" ? "default" : "secondary"}
          className="px-3 py-1 text-sm font-medium"
        >
          {formatCategory(email.category)}
        </Badge>

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Confiança:</span>
          <Progress value={email.confidence_score} className="w-24 h-2" />
          <span className="text-sm font-semibold">{Math.round(email.confidence_score)}%</span>
        </div>
      </div>

      <Tabs defaultValue="content">
        <TabsList>
          <TabsTrigger value="content" className="font-medium">Conteúdo Original</TabsTrigger>
          <TabsTrigger value="response" className="font-medium">Resposta Sugerida</TabsTrigger>
        </TabsList>
        <TabsContent value="content">
          <Card>
            <CardContent className="p-4">
              <pre className="email-content whitespace-pre-wrap">{email.content}</pre>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="response">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="card-title text-base">Sugestão de resposta</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <pre className="email-content whitespace-pre-wrap">{email.suggested_response}</pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
