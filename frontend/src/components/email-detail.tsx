"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Progress } from "@/components/ui/progress";
import { formatCategory } from "@/lib/utils";
import { AlertCircle } from "lucide-react";
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

  useEffect(() => {
    async function fetchEmailDetails() {
      try {
        const apiUrl = API_URLS.EMAIL_DETAIL(id);
        console.log(`Buscando detalhes do email ${id} em: ${apiUrl}`);

        const response = await fetch(apiUrl);

        if (!response.ok) {
          // Check if this is a schema error
          const errorText = await response.text();
          if (errorText.includes("has no column named")) {
            console.error("Database schema error:", errorText);
            throw new Error("Erro de esquema do banco de dados. Execute as migrações do backend.");
          } else {
            // Try to parse as JSON if possible
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
        setEmail(data);
        setError(null);
      } catch (error) {
        console.error("Erro ao carregar detalhes do email:", error);
        setError(error instanceof Error ? error.message : "Erro desconhecido");
        toast.error("Erro ao carregar detalhes", {
          description: "Não foi possível obter os detalhes deste email do servidor.",
        });
      } finally {
        setLoading(false);
      }
    }

    fetchEmailDetails();
  }, [id]);

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

      <div className="flex items-center gap-4">
        <Badge
          variant={email.category === "productive" ? "default" : "secondary"}
          className="px-3 py-1 text-sm"
        >
          {formatCategory(email.category)}
        </Badge>

        <div className="flex items-center gap-2">
          <span className="text-sm">Confiança:</span>
          <Progress value={email.confidence_score} className="w-24 h-2" />
          <span className="text-sm">{Math.round(email.confidence_score)}%</span>
        </div>
      </div>

      <Tabs defaultValue="content">
        <TabsList>
          <TabsTrigger value="content">Conteúdo Original</TabsTrigger>
          <TabsTrigger value="response">Resposta Sugerida</TabsTrigger>
        </TabsList>
        <TabsContent value="content">
          <Card>
            <CardContent className="p-4">
              <pre className="whitespace-pre-wrap font-sans">{email.content}</pre>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="response">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Sugestão de resposta</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <pre className="whitespace-pre-wrap font-sans">{email.suggested_response}</pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
