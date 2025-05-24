// API URLs
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://email-classifier-ahag.onrender.com';

export const API_URLS = {
  STATUS: `${API_BASE_URL}/api/status/`,
  USAGE: `${API_BASE_URL}/api/usage/`,
  API_USAGE: `${API_BASE_URL}/api/usage/`,
  SUBMIT_EMAIL: `${API_BASE_URL}/api/submit-email/`,
  EMAILS_LIST: `${API_BASE_URL}/api/emails/`,
  EMAIL_DETAIL: (id: string) => `${API_BASE_URL}/api/emails/${id}/`,
  JOB_STATUS: (jobId: string) => `${API_BASE_URL}/api/jobs/${jobId}/`,
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

export async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 10000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Tipos para a resposta da API de emails
export interface EmailListResponse {
  emails: Email[];
  count: number;
  user_ip: string;
  success: boolean;
  debug_info?: {
    total_found: number;
    user_ip_used: string;
    headers_checked: {
      x_forwarded_for: string;
      x_real_ip: string;
      remote_addr: string;
    };
  };
  error?: string;
}

export interface Email {
  id: number;
  subject: string;
  sender: string;
  category: string;
  created_at: string;
  confidence_score: number;
  content?: string;
  suggested_response?: string;
}

// Função para buscar emails com tratamento robusto
export async function fetchEmails(): Promise<EmailListResponse> {
  try {
    const response = await fetchWithTimeout(API_URLS.EMAILS_LIST, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    }, 15000); // 15 segundos de timeout

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Erro na API: ${response.status} - ${errorText}`);
      throw new Error(`Erro HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();

    // Validar estrutura da resposta
    if (typeof data !== 'object' || data === null) {
      throw new Error('Resposta inválida da API: não é um objeto');
    }

    // Se não tem a propriedade success, assumir que é o formato antigo
    if (!('success' in data)) {
      // Tentar identificar se é um array de emails diretamente
      if (Array.isArray(data)) {
        return {
          emails: data,
          count: data.length,
          user_ip: 'unknown',
          success: true
        };
      }
      throw new Error('Formato de resposta não reconhecido');
    }

    // Garantir que emails seja sempre um array
    if (!Array.isArray(data.emails)) {
      console.warn('Campo emails não é um array, usando array vazio');
      data.emails = [];
    }

    return data as EmailListResponse;

  } catch (error) {
    console.error('Erro ao buscar emails:', error);

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Erro de conectividade: não foi possível conectar ao servidor');
    }

    throw error;
  }
}
