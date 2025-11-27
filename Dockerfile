FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Definir argumentos de build
ARG APP_ENV=production
ARG UID=1000
ARG GID=1000

# Configurações de ambiente para uv
ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Configurações Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Configurações de timezone
ENV TZ=America/Sao_Paulo

# Instalar dependências do sistema e criar usuário
RUN apt-get update && apt-get install -y \
    curl \
    tzdata \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g $GID appuser \
    && useradd -u $UID -g $GID -m -s /bin/bash appuser

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração do uv primeiro (para cache de layers)
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Instalar dependências
RUN uv sync --no-dev

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretórios necessários
# RUN mkdir -p /app/logs /app/static /app/media
RUN chown -R appuser:appuser /app

# Mudança para usuário não-root
USER appuser

# Expor porta
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Criar script de inicialização 
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Comando padrão
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
