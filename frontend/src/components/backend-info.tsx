"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CircleOff, CheckCircle, Info, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

// Garanta que todas as URLs terminem com barra
const API_BACKEND = process.env.NEXT_PUBLIC_API_BACKEND || '';
const API_BACKEND_STATUS = process.env.NEXT_PUBLIC_API_BACKEND_STATUS || `${API_BACKEND}/api/status/`;

export function BackendInfo() {
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "loading" | "error">("loading");
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    async function checkBackendStatus() {
      try {
        console.log(`Verificando status em: ${API_BACKEND_STATUS}`);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 segundo timeout

        const response = await fetch(API_BACKEND_STATUS, {
          method: "GET",
          headers: {
            "Accept": "application/json",
            "Origin": window.location.origin,
            "Cache-Control": "no-cache", // Evitar cache
          },
          signal: controller.signal,
          cache: 'no-cache',
          mode: 'cors',
          credentials: 'omit', // Não enviar cookies para simplificar
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          const data = await response.json();
          console.log("Status da API:", data);
          setBackendStatus("online");
          setErrorMessage("");
          setLastCheck(new Date());
        } else {
          console.error(`Status código: ${response.status}`);
          setBackendStatus("offline");
          setErrorMessage(`HTTP ${response.status}`);
          setLastCheck(new Date());

          if (!localStorage.getItem('backend-warning-shown')) {
            toast.warning("Backend offline", {
              description: `Servidor retornou ${response.status}: ${response.statusText}`
            });
            localStorage.setItem('backend-warning-shown', 'true');
          }
        }
      } catch (error) {
        console.error("Erro ao verificar status do backend:", error);

        if (error instanceof Error) {
          let errorMsg = error.message;

          // Melhor tratamento para erros comuns
          if (error.name === 'AbortError') {
            errorMsg = "Tempo esgotado";
          } else if (errorMsg.includes('Failed to fetch')) {
            errorMsg = "Erro de conexão";
          } else if (errorMsg.includes('NetworkError')) {
            errorMsg = "Erro de rede";
          } else if (errorMsg.includes('CORS')) {
            errorMsg = "Erro de CORS";
          }

          setErrorMessage(errorMsg);
        } else {
          setErrorMessage("Erro desconhecido");
        }

        setBackendStatus("error");
        setLastCheck(new Date());

        // Enviar apenas uma notificação de erro
        if (!localStorage.getItem('backend-error-shown')) {
          toast.error("Erro de conexão", {
            description: "Não foi possível conectar ao servidor backend. Verifique sua conexão com a internet ou o status do servidor."
          });
          localStorage.setItem('backend-error-shown', 'true');

          // Resetar os avisos após 5 minutos
          setTimeout(() => {
            localStorage.removeItem('backend-error-shown');
            localStorage.removeItem('backend-warning-shown');
          }, 5 * 60 * 1000);
        }
      }
    }

    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000); // Verificar a cada 30 segundos

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    switch (backendStatus) {
      case "loading":
        return <Badge variant="outline" className="animate-pulse">Verificando...</Badge>;
      case "online":
        return (
          <Badge className="bg-green-500">
            <CheckCircle className="h-3 w-3 mr-1" /> Online
          </Badge>
        );
      case "offline":
        return (
          <Badge variant="destructive">
            <CircleOff className="h-3 w-3 mr-1" /> Offline
          </Badge>
        );
      case "error":
        return (
          <Badge variant="destructive">
            <AlertTriangle className="h-3 w-3 mr-1" /> Erro
          </Badge>
        );
      default:
        return null;
    }
  };

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
            {getStatusIcon()}
          </div>

          {errorMessage && (
            <div className="text-sm text-red-600">
              Erro: {errorMessage}
            </div>
          )}

          {lastCheck && (
            <div className="text-xs text-muted-foreground">
              Última verificação: {lastCheck.toLocaleTimeString()}
            </div>
          )}

          <div className="rounded-md bg-muted p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <Info className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium">API disponível em:</h3>
                <div className="mt-2 text-sm text-muted-foreground">
                  <p className="break-all">{API_BACKEND}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-md bg-green-50 p-4 border border-green-200">
            <div className="flex">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Privacidade garantida</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>Seus emails são isolados automaticamente. Apenas você pode visualizar os emails que classificar.</p>
                </div>
              </div>
            </div>
          </div>

          {backendStatus === "error" && (
            <div className="rounded-md bg-amber-50 p-4 border border-amber-200">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-amber-800">Problemas de conectividade</h3>
                  <div className="mt-2 text-sm text-amber-700">
                    <p>Verifique se o servidor Railway está ativo e funcionando corretamente.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
