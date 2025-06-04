"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { API_URLS } from "@/lib/api-helpers";
import { Clock, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useSystemStatus } from "@/components/system-notice-tooltip";

interface QueueJob {
  id: string;
  job_type: string;
  status: string;
  position_in_queue: number;
  estimated_wait_time: number | null;
  created_at: string;
}

interface QueueStats {
  queue_length: number;
  active_job: QueueJob | null;
  estimated_wait: number;
  queued_jobs: QueueJob[];
  processing_count: number;
}

export function QueueStatusDialog() {
  const { isSystemDisabled } = useSystemStatus();
  const [queueStats, setQueueStats] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchQueueStats = async () => {
    if (isSystemDisabled) {
      setError("Sistema desabilitado");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(API_URLS.USAGE);

      if (!response.ok) {
        throw new Error(`Falha ao obter estatísticas da fila: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.job_queue) {
        setQueueStats(data.job_queue);
        setError(null);
      } else {
        throw new Error("Formato de dados inválido");
      }
    } catch (error) {
      console.error("Erro ao carregar estatísticas da fila:", error);
      setError(error instanceof Error ? error.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchQueueStats();

      // Atualizar a cada 3 segundos quando o diálogo estiver aberto
      const interval = setInterval(fetchQueueStats, 3000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  // Formatação da data para exibição
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };

  // Ícone baseado no status
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 text-amber-500 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
      case 'expired':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex gap-2 items-center"
          disabled={isSystemDisabled}
        >
          <Clock className="h-4 w-4" />
          Status da Fila
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Status da Fila de Processamento</DialogTitle>
          <DialogDescription>
            {isSystemDisabled
              ? "Fila indisponível - sistema temporariamente desabilitado"
              : "Informações em tempo real sobre jobs em fila e processamento"
            }
          </DialogDescription>
        </DialogHeader>

        {isSystemDisabled ? (
          <div className="bg-amber-50 dark:bg-amber-950/50 p-4 rounded-md border border-amber-200 dark:border-amber-800">
            <div className="text-amber-800 dark:text-amber-200 text-sm">
              A fila de processamento não está disponível pois o backend foi temporariamente desabilitado devido aos custos operacionais.
            </div>
          </div>
        ) : loading && !queueStats ? (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="bg-destructive/10 p-4 rounded-md text-destructive text-sm">
            Erro ao carregar dados: {error}
          </div>
        ) : queueStats ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-muted/50 p-3 rounded-md">
                <div className="text-xs text-muted-foreground">Total na fila</div>
                <div className="text-2xl font-bold">{queueStats.queue_length}</div>
              </div>
              <div className="bg-muted/50 p-3 rounded-md">
                <div className="text-xs text-muted-foreground">Tempo estimado</div>
                <div className="text-2xl font-bold">
                  {queueStats.estimated_wait}s
                </div>
              </div>
            </div>

            {queueStats.active_job && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Job sendo processado:</h4>
                <div className="bg-blue-50 p-3 rounded-md border border-blue-100">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                    <span className="font-medium">{queueStats.active_job.job_type}</span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    ID: {queueStats.active_job.id.substring(0, 12)}...
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Iniciado em: {formatDate(queueStats.active_job.created_at)}
                  </div>
                  <Progress className="h-1 mt-2" value={50} />
                </div>
              </div>
            )}

            {queueStats.queued_jobs && queueStats.queued_jobs.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Próximos na fila:</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {queueStats.queued_jobs.map((job) => (
                    <div key={job.id} className="bg-muted/40 p-2 rounded-md border border-muted">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <span className="text-sm font-medium">{job.job_type}</span>
                        </div>
                        <span className="text-xs bg-muted px-2 py-0.5 rounded-full">
                          #{job.position_in_queue}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
                        <span>ID: {job.id.substring(0, 8)}...</span>
                        <span>
                          Espera: {job.estimated_wait_time || '?'}s
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {queueStats.queued_jobs.length === 0 && !queueStats.active_job && (
              <div className="text-center py-4 text-muted-foreground">
                Não há jobs em processamento no momento
              </div>
            )}

            <div className="text-xs text-muted-foreground text-right">
              Última atualização: {new Date().toLocaleTimeString()}
            </div>
          </div>
        ) : null}

        <div className="flex justify-between mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchQueueStats()}
            disabled={isSystemDisabled}
          >
            Atualizar Dados
          </Button>
          <Button variant="default" size="sm" onClick={() => setIsOpen(false)}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
