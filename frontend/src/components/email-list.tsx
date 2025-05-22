"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { ptBR } from "date-fns/locale";
import { formatCategory } from "@/lib/utils";
import { API_URLS } from "@/lib/api-helpers";

interface Email {
  id: number;
  subject: string;
  sender: string;
  category: string;
  created_at: string;
  confidence_score: number;
}

export default function EmailList() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchEmails() {
      try {
        console.log(`Buscando emails em: ${API_URLS.EMAILS_LIST}`);

        const response = await fetch(API_URLS.EMAILS_LIST);

        if (!response.ok) {
          throw new Error("Falha ao buscar emails");
        }

        const data = await response.json();
        console.log(`${data.length} emails recebidos do servidor`);
        setEmails(data);
      } catch (error) {
        console.error("Erro ao carregar emails:", error);
        toast.error("Erro ao carregar a lista de emails", {
          description: "Não foi possível obter a lista de emails do servidor.",
        });
      } finally {
        setLoading(false);
      }
    }

    fetchEmails();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <Skeleton className="h-6 w-3/4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-4 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2" />
              <div className="flex justify-between items-center mt-4">
                <Skeleton className="h-6 w-24" />
                <Skeleton className="h-4 w-32" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="text-center py-10">
        <h3 className="text-lg font-medium mb-2">Nenhum email classificado</h3>
        <p className="text-muted-foreground mb-6">Submeta um email para começar.</p>
        <Link href="/">
          <Button>Voltar para página inicial</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {emails.map((email) => (
        <Link href={`/emails/${email.id}`} key={email.id}>
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold truncate">{email.subject}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">De: {email.sender}</p>
              <div className="flex justify-between items-center mt-4">
                <Badge
                  variant={email.category === "productive" ? "default" : "secondary"}
                >
                  {formatCategory(email.category)}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(email.created_at), { addSuffix: true, locale: ptBR })}
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
