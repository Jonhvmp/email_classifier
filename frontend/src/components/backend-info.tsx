"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CircleOff, CheckCircle, Info } from "lucide-react";
import { toast } from "sonner";

// Garanta que todas as URLs terminem com barra
const API_BACKEND = process.env.NEXT_PUBLIC_API_BACKEND || "http://localhost:8000";
const API_BACKEND_STATUS = process.env.NEXT_PUBLIC_API_BACKEND_STATUS || "http://localhost:8000/api/status/";

export function BackendInfo() {
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "loading">("loading");

  useEffect(() => {
    async function checkBackendStatus() {
      try {
        console.log(`Verificando status em: ${API_BACKEND_STATUS}`);

        const response = await fetch(API_BACKEND_STATUS, {
          method: "GET",
          // Simplificando os cabeçalhos para evitar problemas de CORS
          headers: { "Accept": "application/json" },
          // Remova credentials se estiver causando problemas
          // credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          console.log("Status da API:", data);
          setBackendStatus("online");
        } else {
          console.error(`Status código: ${response.status}`);
          setBackendStatus("offline");
          toast.warning("Backend offline", {
            description: "O servidor backend não está respondendo. Algumas funcionalidades podem não funcionar corretamente."
          });
        }
      } catch (error) {
        console.error("Erro ao verificar status do backend:", error);
        setBackendStatus("offline");
        toast.warning("Backend offline", {
          description: "O servidor backend não está respondendo. Algumas funcionalidades podem não funcionar corretamente."
        });
      }
    }

    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000); // Verificar a cada 30 segundos

    return () => clearInterval(interval);
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Informações do Sistema</CardTitle>
        <CardDescription>Status do servidor e API</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Status do Backend:</span>
            {backendStatus === "loading" ? (
              <Badge variant="outline" className="animate-pulse">Verificando...</Badge>
            ) : backendStatus === "online" ? (
              <Badge className="bg-green-500">
                <CheckCircle className="h-3 w-3 mr-1" /> Online
              </Badge>
            ) : (
              <Badge variant="destructive">
                <CircleOff className="h-3 w-3 mr-1" /> Offline
              </Badge>
            )}
          </div>

          <div className="rounded-md bg-muted p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <Info className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium">API disponível em:</h3>
                <div className="mt-2 text-sm text-muted-foreground">
                  <p>{API_BACKEND}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
