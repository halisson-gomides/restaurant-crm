#!/bin/bash
set -e

echo "🚀 Iniciando aplicação..."

# Aguardar banco de dados estar disponível
echo "📊 Aguardando banco de dados..."
until pg_isready -h postgres -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -q; do
    echo "PostgreSQL não está pronto... aguardando 2s"
    sleep 2
done

echo "✅ Banco de dados disponível!"

# Executar migrações do Alembic
echo "🔄 Executando migrações do banco de dados..."
uv run alembic upgrade head

# Verificar se as migrações foram aplicadas com sucesso
if [ $? -eq 0 ]; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "❌ Erro ao aplicar migrações!"
    exit 1
fi

# Executar comando passado como argumentos
echo "🌟 Iniciando aplicação..."
exec "$@"
