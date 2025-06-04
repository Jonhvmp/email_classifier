"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { API_URLS } from "@/lib/api-helpers";
import { Server, Database, CheckCircle, XCircle } from "lucide-react";
import { useSystemStatus } from "@/components/system-notice-tooltip";

interface BackendStatus {
  status: string;
  message: string;
  version: string;
  database: {
    status: string;
    engine: string;
  };
  debug_mode: boolean;
}

export function BackendInfo() {
  const { isSystemDisabled } = useSystemStatus();
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(API_URLS.STATUS);
        if (!response.ok) throw new Error("Falha ao conectar com o backend");
        const data = await response.json();
        setStatus(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    };

    if (isSystemDisabled) {
      setStatus(null);
      setError("Sistema temporariamente desabilitado");
      setLoading(false);
      return;
    }

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Atualizar a cada 30 segundos

    return () => clearInterval(interval);
  }, [isSystemDisabled]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Status do Backend
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardContent>
      </Card>
    );
  }

  if (error || isSystemDisabled) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Status do Backend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <XCircle className="h-4 w-4" />
              <span>{isSystemDisabled ? "Sistema Desabilitado" : `Erro: ${error}`}</span>
            </div>
            {isSystemDisabled && (
              <div className="text-xs text-muted-foreground">
                O backend foi desligado temporariamente devido aos custos operacionais.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          Status do Backend
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span>Status do Servidor:</span>
          <Badge variant={status?.status === "online" ? "default" : "destructive"}>
            {status?.status === "online" ? (
              <CheckCircle className="w-3 h-3 mr-1" />
            ) : (
              <XCircle className="w-3 h-3 mr-1" />
            )}
            {status?.status === "online" ? "Online" : "Offline"}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span>Banco de Dados:</span>
          <Badge variant={status?.database.status === "connected" ? "default" : "destructive"}>
            <Database className="w-3 h-3 mr-1" />
            {status?.database.status === "connected" ? "Conectado" : "Desconectado"}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span>Versão:</span>
          <span className="text-sm font-mono">{status?.version}</span>
        </div>

        <div className="flex items-center justify-between">
          <span>Modo Debug:</span>
          <Badge variant={status?.debug_mode ? "secondary" : "outline"}>
            {status?.debug_mode ? "Ativo" : "Inativo"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
