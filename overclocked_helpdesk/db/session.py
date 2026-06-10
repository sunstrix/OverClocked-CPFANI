from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from overclocked_helpdesk.config import settings

# =============================================================================
# CONFIGURACAO DO BANCO DE DADOS - SQLITE OTIMIZADO PARA WINDOWS
# =============================================================================

# Configuracao especifica para SQLite
# - check_same_thread=False: Permite uso em aplicacoes assincronas e multi-thread
# - timeout=30: Evita erros de "database is locked" em operacoes concorrentes
# - StaticPool: Mantem conexao unica para SQLite em memoria (se aplicavel)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # Timeout de 30 segundos para evitar locks
    },
    # Para SQLite em arquivo, usamos pool classico
    # Para SQLite em memoria, usaríamos StaticPool
    poolclass=StaticPool if "memory" in settings.DATABASE_URL else None,
    echo=settings.DATABASE_ECHO  # Log de queries SQL (controlado via config.py)
)


# =============================================================================
# OTIMIZACOES ESPECIFICAS PARA SQLITE
# =============================================================================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Configura pragmas do SQLite para melhor performance e integridade.
    Executado automaticamente em cada nova conexao com o banco.
    """
    cursor = dbapi_connection.cursor()
    
    # WAL (Write-Ahead Logging): Permite leituras concorrentes sem bloquear escritas
    # Melhora significativamente a performance em aplicacoes web
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Synchronous=NORMAL: Balance entre performance e seguranca
    # FULL seria mais seguro mas mais lento, OFF seria rapido mas arriscado
    cursor.execute("PRAGMA synchronous=NORMAL")
    
    # Cache size: Aumenta cache de paginas em memoria (padrao e 2000)
    # 10000 paginas = ~40MB de cache (melhor para consultas frequentes)
    cursor.execute("PRAGMA cache_size=10000")
    
    # Foreign keys: Habilita verificacao de chaves estrangeiras
    # SQLite desabilita por padrao, mas e essencial para integridade referencial
    cursor.execute("PRAGMA foreign_keys=ON")
    
    # Busy timeout: Tempo de espera quando banco esta bloqueado (30 segundos)
    cursor.execute("PRAGMA busy_timeout=30000")
    
    cursor.close()


# =============================================================================
# SESSAO DO BANCO DE DADOS
# =============================================================================

# Fabrica de sessoes do SQLAlchemy
# - autocommit=False: Controle manual de transacoes (recomendado)
# - autoflush=False: Flush manual antes de queries (evita efeitos colaterais)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Classe base para todos os modelos ORM
# Todos os modelos devem herdar desta classe
Base = declarative_base()


# =============================================================================
# DEPENDENCIA DE INJECAO DE SESSAO (PARA FASTAPI)
# =============================================================================

def get_db():
    """
    Gerador que fornece uma sessao de banco de dados para cada requisicao.
    Garante que a sessao seja fechada corretamente apos o uso, mesmo em caso de erro.
    
    Uso no FastAPI:
        @app.get("/exemplo")
        def exemplo(db: Session = Depends(get_db)):
            # Use db aqui
            pass
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Em caso de erro, faz rollback automatico
        db.rollback()
        # Log do erro para diagnostico (em producao, usar logger adequado)
        print(f"[ERRO BANCO] Falha na operacao: {str(e)}")
        raise
    finally:
        # Garante que a sessao seja sempre fechada
        db.close()


# =============================================================================
# FUNCOES AUXILIARES PARA MANIPULACAO DO BANCO
# =============================================================================

def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas definidas nos modelos.
    Deve ser chamado na inicializacao da aplicacao.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("[BANCO] Tabelas criadas/verificadas com sucesso.")
    except Exception as e:
        print(f"[ERRO BANCO] Falha ao criar tabelas: {str(e)}")
        raise


def drop_db():
    """
    Remove todas as tabelas do banco de dados.
    USE COM CAUTELA - Esta operacao e irreversivel!
    Util apenas em ambiente de desenvolvimento/testes.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("[BANCO] Todas as tabelas foram removidas.")
    except Exception as e:
        print(f"[ERRO BANCO] Falha ao remover tabelas: {str(e)}")
        raise