import os

class Settings:
    DATABASE_URL=os.getenv('DATABASE_URL','postgresql+asyncpg://hamylion:hamylion@postgres:5432/hamylion')
    REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
    API_KEY=os.getenv('HAMYLION_API_KEY','')
    GITHUB_WEBHOOK_SECRET=os.getenv('GITHUB_WEBHOOK_SECRET','')
    GITHUB_ALLOWED_REPOSITORIES={x.strip().lower() for x in os.getenv('HAMYLION_GITHUB_ALLOWED_REPOSITORIES','').split(',') if x.strip()}
    MAX_RETRIES=int(os.getenv('MAX_RETRIES','5'))
    RETRY_BASE_SECONDS=float(os.getenv('RETRY_BASE_SECONDS','2'))
    RETRY_MAX_SECONDS=float(os.getenv('RETRY_MAX_SECONDS','300'))
    WORKER_NAME=os.getenv('HAMYLION_WORKER_NAME','worker-1')
    RECOVERY_IDLE_MS=int(os.getenv('RECOVERY_IDLE_MS','30000'))
    OUTBOUND_ALLOWED_HOSTS={h.strip().lower() for h in os.getenv('HAMYLION_OUTBOUND_ALLOWED_HOSTS','').split(',') if h.strip()}
    OUTBOUND_TIMEOUT_SECONDS=float(os.getenv('HAMYLION_OUTBOUND_TIMEOUT_SECONDS','10'))
    OUTBOUND_MAX_RESPONSE_BYTES=int(os.getenv('HAMYLION_OUTBOUND_MAX_RESPONSE_BYTES','1048576'))
    WEBHOOK_MAX_BODY_BYTES=int(os.getenv('HAMYLION_WEBHOOK_MAX_BODY_BYTES','2097152'))

settings=Settings()
