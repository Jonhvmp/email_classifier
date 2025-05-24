"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { API_URLS } from "@/lib/api-helpers";
import { Activity, Clock, Calendar } from "lucide-react";

interface UsageStats {
  gemini_api: {
    minute_usage: number;
    minute_limit: number;
    minute_percent: number;
    day_usage: number;
    day_limit: number;
    day_percent: number;
  };
  job_queue: {
    queue_length: number;
    processing_count: number;
  };
}

export function ApiUsageMonitor() {
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(API_URLS.USAGE);
        if (!response.ok) throw new Error("Falha ao buscar estatísticas");
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Atualizar a cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Uso da API
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Uso da API
          </CardTitle>
        </CardHeader>
        <CardContent>
          <span className="text-red-600 text-sm">Erro: {error}</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Uso da API
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span className="text-sm">Por Minuto</span>
            </div>
            <span className="text-sm font-mono">
              {stats?.gemini_api.minute_usage}/{stats?.gemini_api.minute_limit}
            </span>
          </div>
          <Progress value={stats?.gemini_api.minute_percent || 0} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">Por Dia</span>
            </div>
            <span className="text-sm font-mono">
              {stats?.gemini_api.day_usage}/{stats?.gemini_api.day_limit}
            </span>
          </div>
          <Progress value={stats?.gemini_api.day_percent || 0} className="h-2" />
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-sm">Fila de Processamento:</span>
          <span className="text-sm font-mono">
            {stats?.job_queue.queue_length || 0} jobs
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
