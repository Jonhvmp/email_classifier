import time
import logging
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Implementa um sistema de rate limiting para APIs.
    Controla tanto o número de requisições por minuto quanto o número total por dia.
    """
    def __init__(self, requests_per_minute=10, requests_per_day=500, name="default"):
        self.name = name
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.minute_requests = []
        self.day_requests = []
        self.lock = threading.RLock()

        # Para estatísticas de uso
        self.total_requests_today = 0
        self.total_requests_minute = 0
        self.reset_day_stats()

        logger.info(f"Rate limiter '{name}' iniciado: {requests_per_minute} req/min, {requests_per_day} req/dia")

    def reset_day_stats(self):
        """Reseta as estatísticas diárias à meia-noite"""
        self.total_requests_today = 0
        self.day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.day_end = self.day_start + timedelta(days=1)

    def _is_new_day(self):
        """Verifica se é um novo dia para resetar contadores"""
        now = datetime.now()
        if now >= self.day_end:
            logger.info(f"Rate limiter '{self.name}': Novo dia iniciado, resetando contadores")
            self.day_requests = []
            self.reset_day_stats()
            return True
        return False

    def _cleanup_old_requests(self):
        """Remove requisições antigas das listas de controle"""
        now = time.time()

        # Remove requisições mais antigas que 1 minuto
        minute_ago = now - 60
        self.minute_requests = [t for t in self.minute_requests if t > minute_ago]

        # Se for um novo dia, o _is_new_day já limpou a lista de requisições diárias

    def can_make_request(self):
        """
        Verifica se podemos fazer mais uma requisição baseado nos limites
        Retorna: (bool, tempo_de_espera_em_segundos)
        """
        with self.lock:
            self._is_new_day()  # Verifica se é um novo dia
            self._cleanup_old_requests()  # Limpa requisições antigas

            # Verifica limite por minuto
            if len(self.minute_requests) >= self.requests_per_minute:
                oldest = self.minute_requests[0]
                wait_time = 60 - (time.time() - oldest)
                wait_time = max(1, int(wait_time))
                return False, wait_time

            # Verifica limite diário
            if len(self.day_requests) >= self.requests_per_day:
                wait_time = int((self.day_end - datetime.now()).total_seconds())
                return False, wait_time

            return True, 0

    def add_request(self):
        """Registra uma nova requisição"""
        with self.lock:
            now = time.time()
            self.minute_requests.append(now)
            self.day_requests.append(now)
            self.total_requests_minute = len(self.minute_requests)
            self.total_requests_today = len(self.day_requests)

            logger.debug(f"Rate limiter '{self.name}': requisição registrada. "
                        f"{self.total_requests_minute}/{self.requests_per_minute} req/min, "
                        f"{self.total_requests_today}/{self.requests_per_day} req/dia")

            # Alerta se estiver chegando perto do limite
            if self.total_requests_today > self.requests_per_day * 0.8:
                logger.warning(f"Rate limiter '{self.name}': {self.total_requests_today} requisições hoje. "
                              f"Aproximando-se do limite diário ({self.requests_per_day})")

    def get_stats(self):
        """Retorna estatísticas de uso atual"""
        with self.lock:
            self._cleanup_old_requests()
            return {
                "name": self.name,
                "minute_usage": len(self.minute_requests),
                "minute_limit": self.requests_per_minute,
                "minute_percent": (len(self.minute_requests) / self.requests_per_minute) * 100 if self.requests_per_minute else 0,
                "day_usage": len(self.day_requests),
                "day_limit": self.requests_per_day,
                "day_percent": (len(self.day_requests) / self.requests_per_day) * 100 if self.requests_per_day else 0,
                "total_today": self.total_requests_today
            }

    def wait_if_needed(self):
        """
        Verifica se podemos fazer mais uma requisição e espera se necessário.
        Retorna True se a requisição pode prosseguir, False se devemos rejeitar.
        """
        can_request, wait_time = self.can_make_request()

        if not can_request:
            if wait_time > 300:  # Se precisar esperar mais de 5 minutos
                logger.warning(f"Rate limiter '{self.name}': Limite atingido, espera necessária: {wait_time}s (rejeitando)")
                return False

            logger.info(f"Rate limiter '{self.name}': Limite atingido, esperando {wait_time}s")
            time.sleep(wait_time)

            # Verificar novamente após esperar
            can_request, _ = self.can_make_request()
            if not can_request:
                logger.warning(f"Rate limiter '{self.name}': Ainda no limite após esperar, rejeitando requisição")
                return False

        self.add_request()
        return True
