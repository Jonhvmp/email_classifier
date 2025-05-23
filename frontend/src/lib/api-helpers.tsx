// API URLs
const API_BASE = process.env.NEXT_PUBLIC_API_BACKEND || 'http://localhost:8000';

export const API_URLS = {
  EMAILS_LIST: `${API_BASE}/api/emails/`,
  EMAIL_DETAIL: (id: string) => `${API_BASE}/api/emails/${id}/`,
  SUBMIT_EMAIL: `${API_BASE}/api/submit-email/`,
  API_STATUS: `${API_BASE}/api/status/`,
  API_USAGE: `${API_BASE}/api/usage/`,
  JOB_STATUS: (jobId: string) => `${API_BASE}/api/jobs/${jobId}/`,
};

// Tipos
export interface JobStatus {
  id: string;
  job_type: string;
  status: "queued" | "processing" | "completed" | "failed" | "expired";
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  position_in_queue: number;
  estimated_wait_time: number | null;
  has_result: boolean;
  has_error: boolean;
  error_message: string | null;
  email?: {
    id: number;
    subject: string;
    category: string;
    confidence_score: number;
    is_processed: boolean;
  };
}

export interface QueueUpdate {
  position: number;
  waitTime: number;
}

interface SubmitOptions {
  maxAttempts?: number;
  interval?: number;
  onUpdate?: (status: JobStatus) => void;
  onQueueUpdate?: (update: QueueUpdate) => void;
}

// Função para submeter email e aguardar o processamento
export async function submitEmailAndWait(
  formData: FormData,
  options: SubmitOptions = {}
) {
  const {
    maxAttempts = 60, // 1 minuto por padrão
    interval = 1000, // 1 segundo entre verificações
    onUpdate,
    onQueueUpdate,
  } = options;

  // Submit o email inicialmente
  const submitResponse = await fetch(API_URLS.SUBMIT_EMAIL, {
    method: 'POST',
    body: formData,
  });

  if (!submitResponse.ok) {
    const errorText = await submitResponse.text();
    try {
      const errorData = JSON.parse(errorText);
      throw new Error(errorData.message || errorData.error || 'Erro ao submeter email');
    } catch {
      throw new Error(`Erro ao submeter email: ${errorText}`);
    }
  }

  const submitData = await submitResponse.json();
  const jobId = submitData.job_id;
  const emailId = submitData.id;

  if (!jobId) {
    throw new Error('Job ID não fornecido pela API');
  }

  // Atualizar informações da fila inicialmente
  if (onQueueUpdate) {
    onQueueUpdate({
      position: submitData.queue_position || 0,
      waitTime: submitData.estimated_wait || 0,
    });
  }

  // Poll para verificar o status até que esteja completo
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const statusResponse = await fetch(API_URLS.JOB_STATUS(jobId));

      if (!statusResponse.ok) {
        console.error(`Erro ao verificar status: ${statusResponse.status}`);
        throw new Error(`Erro ao verificar status do job: ${statusResponse.status}`);
      }

      const jobStatus: JobStatus = await statusResponse.json();

      // Notificar sobre a atualização
      if (onUpdate) {
        onUpdate(jobStatus);
      }

      // Atualizar informação da posição na fila
      if (onQueueUpdate && jobStatus.status === 'queued') {
        onQueueUpdate({
          position: jobStatus.position_in_queue,
          waitTime: jobStatus.estimated_wait_time || 0,
        });
      }

      // Verificar se o job foi concluído
      if (jobStatus.status === 'completed') {
        // Verificar se o email foi processado
        if (jobStatus.email && jobStatus.email.is_processed) {
          // Retornar os dados do email
          return {
            emailId: emailId,
            job_id: jobId,
            ...jobStatus.email
          };
        } else {
          // O job foi concluído, mas o email ainda pode estar em processamento
          console.log('Job concluído, aguardando processamento final do email...');
          // Continuar o polling para verificar o status do email
        }
      }

      // Verificar se houve algum erro
      if (jobStatus.status === 'failed' || jobStatus.status === 'expired') {
        throw new Error(jobStatus.error_message || `Job falhou com status: ${jobStatus.status}`);
      }

      // Esperar o intervalo antes da próxima verificação
      await new Promise(resolve => setTimeout(resolve, interval));

    } catch (error) {
      console.error('Erro ao verificar status:', error);
      throw error;
    }
  }

  // Se chegamos aqui, atingimos o número máximo de tentativas
  throw new Error(`Tempo limite excedido após ${maxAttempts} tentativas`);
}
