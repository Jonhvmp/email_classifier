"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Server, Database, Clock, AlertCircle, CheckCircle } from "lucide-react";
import { API_URLS } from "@/lib/api-helpers";

interface BackendStatus {
  status: string;
  message: string;
  version: string;
  timestamp: string;
  server_info: {
    python_version: string;
    django_version: string;
    environment: string;
    port: string;
  };
  database: {
    status: string;
    engine: string;
  };
  job_queue: string;
  debug_mode: boolean;
}

export function BackendInfo() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchBackendStatus() {
    try {
      const response = await fetch(API_URLS.API_STATUS);

      if (!response.ok) {
        throw new Error(`Falha ao obter status: ${response.status}`);
      }

      const data = await response.json();
      setBackendStatus(data);
      setError(null);
    } catch (error) {
      console.error("Erro ao carregar status do backend:", error);
      setError(error instanceof Error ? error.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchBackendStatus();

    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Status do Backend</CardTitle>
          <CardDescription>Carregando informações...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (error || !backendStatus) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Status do Backend</CardTitle>
          <CardDescription>Informações não disponíveis</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error || "Não foi possível conectar com o backend"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const isOnline = backendStatus.status === "online";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          Status do Backend
        </CardTitle>
        <CardDescription>
          Informações do servidor e sistema
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status</span>
          <Badge variant={isOnline ? "default" : "destructive"} className="flex items-center gap-1">
            {isOnline ? (
              <CheckCircle className="h-3 w-3" />
            ) : (
              <AlertCircle className="h-3 w-3" />
            )}
            {isOnline ? "Online" : "Offline"}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Versão</span>
          <span className="text-sm font-mono">{backendStatus.version}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Ambiente</span>
          <Badge variant="outline" className="text-xs">
            {backendStatus.server_info.environment}
          </Badge>
        </div>

        <div className="pt-2 border-t">
          <div className="flex items-center gap-2 mb-2">
            <Database className="h-4 w-4" />
            <span className="text-sm font-medium">Banco de Dados</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Status:</span>
            <Badge
              variant={backendStatus.database.status === "connected" ? "default" : "destructive"}
              className="text-xs"
            >
              {backendStatus.database.status === "connected" ? "Conectado" : "Desconectado"}
            </Badge>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-sm">Engine:</span>
            <span className="text-xs font-mono">{backendStatus.database.engine}</span>
          </div>
        </div>

        <div className="pt-2 border-t">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-medium">Sistema</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Django:</span>
            <span className="text-xs font-mono">{backendStatus.server_info.django_version}</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-sm">Porta:</span>
            <span className="text-xs font-mono">{backendStatus.server_info.port}</span>
          </div>
        </div>

        {backendStatus.debug_mode && (
          <Alert className="bg-yellow-50 border-yellow-200 text-yellow-800">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              Modo debug ativo (desenvolvimento)
            </AlertDescription>
          </Alert>
        )}

        <p className="text-xs text-muted-foreground">
          Última atualização: {new Date(backendStatus.timestamp).toLocaleTimeString()}
        </p>
      </CardContent>
    </Card>
  );
}
