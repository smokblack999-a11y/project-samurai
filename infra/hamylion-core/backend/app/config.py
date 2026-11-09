import os

class Settings:
    DATABASE_URL=os.getenv('DATABASE_URL','postgresql+asyncpg://hamylion:hamylion@postgres:5432/hamylion')
    REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
    API_KEY=os.getenv('HAMYLION_API_KEY','')
    MAX_RETRIES=int(os.getenv('MAX_RETRIES','5'))
    RETRY_BASE_SECONDS=float(os.getenv('RETRY_BASE_SECONDS','1'))
    DELIVERY_TIMEOUT_SECONDS=int(os.getenv('DELIVERY_TIMEOUT_SECONDS','30'))
    RETRY_MAX_SECONDS=float(os.getenv('RETRY_MAX_SECONDS','60'))
    AUTO_CREATE_SCHEMA=os.getenv('AUTO_CREATE_SCHEMA','false').lower()=='true'
    RATE_LIMIT_PER_MINUTE=int(os.getenv('RATE_LIMIT_PER_MINUTE','600'))
    WS_TOKEN_SECRET=os.getenv('WS_TOKEN_SECRET','')
    OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
    AEGIS_MODEL=os.getenv('AEGIS_MODEL','gpt-6-sol')
    AEGIS_CYBER_PROGRAM=os.getenv('AEGIS_CYBER_PROGRAM','standard').lower()
    AEGIS_INTERNAL_SECURITY_ONLY=os.getenv('AEGIS_INTERNAL_SECURITY_ONLY','false').lower()=='true'
    AEGIS_TIMEOUT_SECONDS=float(os.getenv('AEGIS_TIMEOUT_SECONDS','45'))

settings=Settings()
