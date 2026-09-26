import os

class Settings:
    DATABASE_URL=os.getenv('DATABASE_URL','postgresql+asyncpg://hamylion:hamylion@postgres:5432/hamylion')
    REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
    API_KEY=os.getenv('HAMYLION_API_KEY','')
    MAX_RETRIES=int(os.getenv('MAX_RETRIES','5'))
    RETRY_BASE_SECONDS=float(os.getenv('RETRY_BASE_SECONDS','2'))
    RETRY_MAX_SECONDS=float(os.getenv('RETRY_MAX_SECONDS','300'))
    WORKER_NAME=os.getenv('HAMYLION_WORKER_NAME','worker-1')
    RECOVERY_IDLE_MS=int(os.getenv('RECOVERY_IDLE_MS','30000'))

settings=Settings()
