import threading
import queue
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable

logger = logging.getLogger(__name__)

class JobStatus:
    """Status possíveis para um job na fila"""
    QUEUED = "queued"        # Na fila, aguardando processamento
    PROCESSING = "processing"  # Em processamento
    COMPLETED = "completed"   # Processado com sucesso
    FAILED = "failed"         # Falhou durante processamento
    EXPIRED = "expired"       # Expirou na fila sem ser processado

class Job:
    """Representa um job individual na fila"""
    def __init__(self, job_type: str, data: Dict[str, Any], callback: Optional[Callable] = None):
        self.id = str(uuid.uuid4())
        self.job_type = job_type
        self.data = data
        self.status = JobStatus.QUEUED
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.callback = callback
        self.position_in_queue = 0  # Será atualizado pelo JobQueue

    def start(self):
        """Marca o job como iniciado"""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()

    def complete(self, result):
        """Marca o job como completo com resultado"""
        self.status = JobStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
        if self.callback:
            try:
                self.callback(self)
            except Exception as e:
                logger.error(f"Erro ao executar callback do job {self.id}: {e}")

    def fail(self, error):
        """Marca o job como falho com erro"""
        self.status = JobStatus.FAILED
        self.error = str(error)
        self.completed_at = datetime.now()
        if self.callback:
            try:
                self.callback(self)
            except Exception as e:
                logger.error(f"Erro ao executar callback do job {self.id}: {e}")

    def expire(self):
        """Marca o job como expirado"""
        self.status = JobStatus.EXPIRED
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict:
        """Converte o job para dicionário para ser retornado via API"""
        wait_time = None
        if self.status == JobStatus.QUEUED:
            # Estimar tempo de espera baseado na posição na fila
            wait_time = self.position_in_queue * 3  # ~3 segundos por job na frente

        processing_time = None
        if self.started_at and self.completed_at:
            processing_time = (self.completed_at - self.started_at).total_seconds()

        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "position_in_queue": self.position_in_queue,
            "estimated_wait_time": wait_time,  # em segundos
            "processing_time": processing_time,  # em segundos
            "has_result": self.result is not None,
            "has_error": self.error is not None,
            "error_message": self.error if self.error else None
        }


class JobQueue:
    """Fila de jobs para processamento"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.queue = queue.PriorityQueue()  # (prioridade, timestamp, job)
        self.jobs = {}  # id -> job
        self.active_job = None
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.job_types = {}  # Registro de manipuladores por tipo de job
        self._initialized = True

        # Iniciar thread de processamento de jobs
        self.start_worker()

    def register_job_type(self, job_type: str, handler: Callable):
        """Registra um manipulador para um tipo de job"""
        self.job_types[job_type] = handler
        logger.info(f"Registrado manipulador para jobs do tipo: {job_type}")

    def enqueue(self, job_type: str, data: Dict[str, Any], priority: int = 1, callback: Optional[Callable] = None) -> str:
        """
        Coloca um job na fila para processamento

        Args:
            job_type: tipo do job (deve ter um manipulador registrado)
            data: dados para processamento
            priority: prioridade do job (menor valor = maior prioridade)
            callback: função a chamar quando o job for concluído

        Returns:
            ID do job
        """
        if job_type not in self.job_types:
            raise ValueError(f"Tipo de job não registrado: {job_type}")

        job = Job(job_type, data, callback)

        with self.lock:
            self.jobs[job.id] = job
            # Atualizar as posições dos jobs na fila
            self._update_queue_positions()

            # Enfileirar com prioridade
            self.queue.put((priority, time.time(), job))
            logger.info(f"Job {job.id} do tipo {job_type} enfileirado com prioridade {priority}")

        return job.id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Obtém um job pelo ID"""
        return self.jobs.get(job_id)

    def get_queue_status(self) -> Dict[str, Any]:
        """Obtém o status atual da fila"""
        with self.lock:
            queued_jobs = [j for j in self.jobs.values() if j.status == JobStatus.QUEUED]
            processing_job = self.active_job

            status = {
                "queue_length": len(queued_jobs),
                "active_job": processing_job.to_dict() if processing_job else None,
                "estimated_wait": len(queued_jobs) * 3,  # ~3 segundos por job
                "queued_jobs": [j.to_dict() for j in queued_jobs[:5]],  # Mostrar no máximo 5 jobs
                "processing_count": 1 if processing_job else 0,
            }

            return status

    def start_worker(self):
        """Inicia o worker thread se não estiver rodando"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.stop_event.clear()
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
            logger.info("Worker thread iniciada para processamento de jobs")

    def stop_worker(self):
        """Para o worker thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            logger.info("Solicitando parada do worker thread...")
            self.stop_event.set()
            self.worker_thread.join(timeout=5.0)
            if self.worker_thread.is_alive():
                logger.warning("Worker thread não parou em tempo hábil!")
            else:
                logger.info("Worker thread parado com sucesso.")

    def _process_queue(self):
        """Loop principal do processamento de jobs"""
        while not self.stop_event.is_set():
            try:
                # Verificar se há jobs na fila
                if self.queue.empty():
                    time.sleep(0.1)  # Evita consumo alto de CPU
                    continue

                # Pegar o próximo job
                _, _, job = self.queue.get(block=False)

                # Verificar se o job é válido
                if job.id not in self.jobs:
                    logger.warning(f"Job {job.id} não encontrado no registro de jobs")
                    continue

                # Atualizar as posições dos jobs na fila
                with self.lock:
                    self.active_job = job
                    self._update_queue_positions()

                # Marcar job como em processamento
                job.start()

                # Verificar se o tipo de job tem um manipulador registrado
                if job.job_type not in self.job_types:
                    job.fail(f"Nenhum manipulador registrado para tipo de job: {job.job_type}")
                    continue

                # Executar o job
                handler = self.job_types[job.job_type]
                logger.info(f"Processando job {job.id} do tipo {job.job_type}")

                try:
                    result = handler(job.data)
                    job.complete(result)
                    logger.info(f"Job {job.id} concluído com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao processar job {job.id}: {e}", exc_info=True)
                    job.fail(e)
                finally:
                    with self.lock:
                        self.active_job = None
                        # Limpar jobs antigos
                        self._cleanup_old_jobs()
                        # Atualizar posições na fila
                        self._update_queue_positions()

            except queue.Empty:
                # Fila vazia, simplesmente continua
                pass
            except Exception as e:
                logger.error(f"Erro no worker thread: {e}", exc_info=True)
                time.sleep(1)  # Evita ciclo rápido em caso de erro

    def _update_queue_positions(self):
        """Atualiza as posições dos jobs na fila"""
        # Isso é uma aproximação, já que PriorityQueue não permite iteração
        # Só chamamos dentro de contextos já protegidos pelo lock
        queued_jobs = [j for j in self.jobs.values() if j.status == JobStatus.QUEUED]
        # Ordenamos por prioridade simulada (poderia ser melhorado)
        # Na prática, a ordem real é determinada pela PriorityQueue
        for i, job in enumerate(queued_jobs):
            job.position_in_queue = i

    def _cleanup_old_jobs(self, max_age_seconds=3600):
        """Limpa jobs concluídos ou falhos antigos"""
        # Só chamamos dentro de contextos já protegidos pelo lock
        current_time = datetime.now()
        to_remove = []

        for job_id, job in self.jobs.items():
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.EXPIRED):
                if job.completed_at:
                    age = (current_time - job.completed_at).total_seconds()
                    if age > max_age_seconds:
                        to_remove.append(job_id)

        for job_id in to_remove:
            del self.jobs[job_id]

        if to_remove:
            logger.debug(f"Removidos {len(to_remove)} jobs antigos")


# Instância global para uso em todo o aplicativo
job_queue = JobQueue()
