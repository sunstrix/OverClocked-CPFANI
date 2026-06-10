from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timezone, timedelta


class Settings(BaseSettings):
    """
    Configuracoes centrais do projeto OverClocked CPFANI.
    Carrega variaveis de ambiente do arquivo .env quando disponivel.
    Todas as mensagens e formatos seguem o padrao brasileiro (pt-BR).
    """

    # ========================================================================
    # IDIOMA E REGIONALIZACAO
    # ========================================================================
    LANG: str = "pt-BR"
    TIMEZONE: timezone = timezone(timedelta(hours=-3), name="America/Sao_Paulo")
    DATE_FORMAT: str = "%d/%m/%Y"
    DATETIME_FORMAT: str = "%d/%m/%Y %H:%M:%S"
    CURRENCY_LOCALE: str = "pt_BR"

    # ========================================================================
    # MENSAGENS DE SISTEMA (pt-BR)
    # ========================================================================
    MESSAGES: dict = {
        "sucesso_operacao": "Operacao realizada com sucesso.",
        "erro_servidor": "Ocorreu um erro interno no servidor. Tente novamente mais tarde.",
        "erro_validacao": "Dados invalidos. Verifique os campos e tente novamente.",
        "erro_autenticacao": "Falha na autenticacao. Credenciais invalidas ou expiradas.",
        "erro_permissao": "Acesso negado. Voce nao tem permissao para realizar esta acao.",
        "erro_recurso_nao_encontrado": "Recurso nao encontrado. Verifique o identificador informado.",
        "erro_banco_dados": "Erro ao acessar o banco de dados. Contate o administrador.",
        "erro_email_envio": "Falha ao enviar e-mail. Verifique as configuracoes SMTP.",
        "erro_slack_envio": "Falha ao enviar notificacao para o Slack.",
        "aviso_manutencao": "Sistema em manutencao programada. Retorne em breve.",
    }

    # ========================================================================
    # MENSAGENS DE VALIDACAO (pt-BR)
    # ========================================================================
    VALIDATION_MESSAGES: dict = {
        "campo_obrigatorio": "Este campo e obrigatorio.",
        "email_invalido": "Formato de e-mail invalido.",
        "telefone_invalido": "Formato de telefone invalido. Use (XX) XXXXX-XXXX.",
        "cpf_invalido": "CPF invalido. Verifique os digitos informados.",
        "senha_curta": "A senha deve ter no minimo 8 caracteres.",
        "senha_sem_requisitos": "A senha deve conter letras e numeros.",
        "data_invalida": "Formato de data invalido. Use DD/MM/AAAA.",
        "valor_negativo": "O valor nao pode ser negativo.",
        "arquivo_grande": "O arquivo excede o tamanho maximo permitido.",
        "tipo_arquivo_invalido": "Tipo de arquivo nao permitido.",
    }

    # ========================================================================
    # CONFIGURACOES DE UPLOAD
    # ========================================================================
    UPLOAD_CONFIG: dict = {
        "max_size_mb": 10,
        "allowed_extensions": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".txt"],
        "upload_folder": "uploads",
    }

    # ========================================================================
    # BANCO DE DADOS
    # ========================================================================
    DATABASE_URL: str = "sqlite:///./helpdesk.db"
    DATABASE_ECHO: bool = False

    # ========================================================================
    # SLACK
    # ========================================================================
    SLACK_BOT_TOKEN: str | None = None
    SLACK_WEBHOOK_URL: str | None = None
    SLACK_CHANNEL_PADRAO: str = "#helpdesk-cpfani"

    # ========================================================================
    # EMAIL - SMTP
    # ========================================================================
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True
    EMAIL_REMETENTE_PADRAO: str = "noreply@cpfani.org.br"
    EMAIL_ASSUNTO_PADRAO: str = "OverClocked CPFANI - Notificacao"

    # ========================================================================
    # SEGURANCA E SESSAO
    # ========================================================================
    SECRET_KEY: str | None = None
    TOKEN_EXPIRACAO_MINUTOS: int = 60
    SENHA_MINIMA_TAMANHO: int = 8

    # ========================================================================
    # LOG E MONITORAMENTO
    # ========================================================================
    LOG_NIVEL: str = "INFO"
    LOG_ARQUIVO: str = "logs/app.log"
    LOG_ROTACAO_DIAS: int = 7

    # ========================================================================
    # CONFIGURACAO DO PYDANTIC SETTINGS
    # ========================================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        arbitrary_types_allowed=True  # Necessario para aceitar timezone como tipo
    )

    # ========================================================================
    # PROPRIEDADES COMPUTADAS
    # ========================================================================
    @property
    def is_producao(self) -> bool:
        """Retorna True se o ambiente for de producao."""
        return self.LOG_NIVEL.upper() not in ["DEBUG", "INFO"]

    @property
    def database_tipo(self) -> str:
        """Retorna o tipo do banco de dados."""
        if self.DATABASE_URL.startswith("sqlite"):
            return "sqlite"
        elif self.DATABASE_URL.startswith("postgresql"):
            return "postgresql"
        elif self.DATABASE_URL.startswith("mysql"):
            return "mysql"
        return "desconhecido"


# Instancia global das configuracoes
settings = Settings()