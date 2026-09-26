import os
class Settings:
    DATABASE_URL=os.getenv('DATABASE_URL','postgresql+asyncpg://hamylion:hamylion@postgres:5432/hamylion')
    REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
    API_KEY=os.getenv('HAMYLION_API_KEY','')
    MAX_RETRIES=int(os.getenv('MAX_RETRIES','5'))
    RETRY_BASE_SECONDS=float(os.getenv('RETRY_BASE_SECONDS','1'))
settings=Settings()
