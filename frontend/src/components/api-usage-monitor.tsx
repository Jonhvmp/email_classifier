"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, Clock, Layers } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { API_URLS } from "@/lib/api-helpers";
import { Badge } from "./ui/badge";

interface ActiveJob {
  id: string;
  job_type: string;
  status: string;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
}

interface QueuedJob {
  id: string;
  job_type: string;
  status: string;
  position_in_queue: number;
  estimated_wait_time: number | null;
  created_at: string;
}

interface ApiUsageStats {
  gemini_api: {
    minute_usage: number;
    minute_limit: number;
    minute_percent: number;
    day_usage: number;
    day_limit: number;
    day_percent: number;
    total_today: number;
  };
  job_queue: {
    queue_length: number;
    active_job: ActiveJob | null;
    estimated_wait: number;
    queued_jobs: QueuedJob[];
    processing_count: number;
  };
  timestamp: string;
}

export function ApiUsageMonitor() {
  const [usageStats, setUsageStats] = useState<ApiUsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchApiUsage() {
    try {
      setLoading(true);

      const response = await fetch(API_URLS.API_USAGE);

      if (!response.ok) {
        throw new Error(`Falha ao obter estatísticas de uso: ${response.status}`);
      }

      const data = await response.json();
      setUsageStats(data);
      setError(null);

    } catch (error) {
      console.error("Erro ao carregar estatísticas de uso da API:", error);
      setError(error instanceof Error ? error.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchApiUsage();

    // Atualizar a cada 5 segundos
    const interval = setInterval(fetchApiUsage, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !usageStats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Uso da API & Fila</CardTitle>
          <CardDescription>Carregando estatísticas...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Uso da API & Fila</CardTitle>
          <CardDescription>Estatísticas não disponíveis</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erro</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!usageStats) {
    return null;
  }

  const { gemini_api, job_queue } = usageStats;
  const isMinuteHigh = gemini_api.minute_percent > 80;
  const isDayHigh = gemini_api.day_percent > 80;
  const hasQueue = job_queue.queue_length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Status do Sistema</CardTitle>
        <CardDescription>Métricas de utilização e fila</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium">Taxa por minuto</span>
            <span className="text-sm font-medium">
              {gemini_api.minute_usage}/{gemini_api.minute_limit}
            </span>
          </div>
          <Progress
            value={gemini_api.minute_percent}
            className={isMinuteHigh ? "bg-amber-100" : ""}
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium">Uso diário</span>
            <span className="text-sm font-medium">
              {gemini_api.day_usage}/{gemini_api.day_limit}
            </span>
          </div>
          <Progress
            value={gemini_api.day_percent}
            className={isDayHigh ? "bg-amber-100" : ""}
          />
        </div>

        <div className="pt-2 border-t">
          <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
            <Layers className="h-4 w-4" />
            Status da Fila
            {job_queue.queue_length > 0 && (
              <Badge variant="secondary" className="ml-2 text-xs">
                {job_queue.queue_length} na fila
              </Badge>
            )}
          </h4>
          <div className="flex justify-between items-center">
            <span className="text-sm">Tamanho da fila:</span>
            <span className="text-sm font-medium">{job_queue.queue_length}</span>
          </div>
          <div className="flex justify-between items-center mt-1">
            <span className="text-sm">Tempo estimado de espera:</span>
            <span className="text-sm font-medium">
              {job_queue.estimated_wait > 0 ? `${job_queue.estimated_wait}s` : 'Imediato'}
            </span>
          </div>
          <div className="flex justify-between items-center mt-1">
            <span className="text-sm">Jobs em processamento:</span>
            <span className="text-sm font-medium">{job_queue.processing_count}</span>
          </div>

          {job_queue.active_job && (
            <div className="mt-2 bg-muted/50 p-2 rounded text-xs">
              <p className="font-medium">Job ativo: {job_queue.active_job.job_type}</p>
              <p className="text-muted-foreground truncate">ID: {job_queue.active_job.id}</p>
            </div>
          )}
        </div>

        {(isMinuteHigh || isDayHigh) && (
          <Alert variant="destructive" className="bg-amber-50 border-amber-200 text-amber-800 mt-2">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Alto uso da API</AlertTitle>
            <AlertDescription>
              A API Gemini está com uso elevado. Algumas requisições podem demorar mais.
            </AlertDescription>
          </Alert>
        )}

        {hasQueue && (
          <Alert variant="default" className="bg-blue-50 border-blue-200 text-blue-800 mt-2">
            <Clock className="h-4 w-4" />
            <AlertTitle>Fila de processamento ativa</AlertTitle>
            <AlertDescription>
              Há {job_queue.queue_length} requisições na fila. O tempo estimado de espera é de {job_queue.estimated_wait} segundos.
            </AlertDescription>
          </Alert>
        )}

        <p className="text-xs text-muted-foreground mt-2">
          Total de requisições hoje: {gemini_api.total_today}
        </p>
      </CardContent>
    </Card>
  );
}
