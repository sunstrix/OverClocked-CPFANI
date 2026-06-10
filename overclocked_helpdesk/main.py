from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from overclocked_helpdesk.config import settings

from overclocked_helpdesk.db.session import SessionLocal, engine, Base, get_db
from overclocked_helpdesk.services.notifier import notify_and_create_query

# ROUTERS
from overclocked_helpdesk.api.queries import router as queries_router
from overclocked_helpdesk.api.qr import router as qr_router
from overclocked_helpdesk.api.admin import router as admin_router

# MODELS
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.models.query import Query
from overclocked_helpdesk.models.team import Team


# =============================================================================
# INICIALIZACAO DA APLICACAO FASTAPI - OVERCLOCKED CPFANI
# Toda a documentacao e mensagens em portugues do Brasil (pt-BR)
# =============================================================================

app = FastAPI(
    title="OverClocked Helpdesk - CPFANI",
    description="Sistema de suporte tecnico para eventos. Registre chamados, acompanhe status e gerencie mentores.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Helpdesk", "description": "Operacoes de abertura e acompanhamento de chamados"},
        {"name": "Mentores", "description": "Gerenciamento de disponibilidade e carga de mentores"},
        {"name": "Equipes", "description": "Consulta de status de chamados por equipe"},
        {"name": "Administracao", "description": "Rotas administrativas do sistema"},
    ]
)

# Montagem de arquivos estaticos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inclusao dos routers da API
app.include_router(qr_router, prefix="/qr", tags=["Helpdesk"])
app.include_router(admin_router, prefix="/admin", tags=["Administracao"])
app.include_router(queries_router, prefix="/queries", tags=["Helpdesk"])

# Criacao das tabelas do banco de dados na inicializacao
Base.metadata.create_all(bind=engine)


# =============================================================================
# FUNCOES AUXILIARES
# =============================================================================

def formatar_data_br(data: datetime) -> str:
    """Formata datetime para padrao brasileiro DD/MM/AAAA HH:MM:SS."""
    if data is None:
        return ""
    return data.astimezone(settings.TIMEZONE).strftime(settings.DATETIME_FORMAT)


def background_notify(team_id: int, issue: str, location: str):
    """
    Tarefa em segundo plano para notificar via Slack e registrar chamado no banco.
    Executada assincronamente para nao bloquear a resposta ao usuario.
    """
    db = SessionLocal()
    try:
        notify_and_create_query(
            db=db,
            team_id=team_id,
            issue=issue,
            location=location
        )
    except Exception as e:
        # Log interno do erro para diagnostico (nao expoe ao usuario final)
        print(f"[ERRO] Falha ao processar chamado da equipe {team_id}: {str(e)}")
    finally:
        db.close()


# =============================================================================
# ROTAS DA INTERFACE DO HELPDESK (HTML)
# =============================================================================

@app.get("/", response_class=HTMLResponse, tags=["Helpdesk"], summary="Formulario de abertura de chamado")
def show_helpdesk_form(request: Request):
    """Exibe o formulario principal para equipes registrarem novos chamados de suporte."""
    return templates.TemplateResponse(
        "helpdesk_form.html",
        {
            "request": request,
            "title": "Abrir Chamado - OverClocked CPFANI",
            "lang": settings.LANG
        }
    )


@app.post("/submit", tags=["Helpdesk"], summary="Envia novo chamado para processamento")
def submit_helpdesk_form(
    background_tasks: BackgroundTasks,
    team_id: int = Form(...),
    issue: str = Form(...),
    location: str = Form(...)
):
    """
    Recebe os dados do formulario e agenda o processamento do chamado.
    Resposta imediata para nao travar a interface do usuario.
    """
    # Log interno para auditoria
    print(f"[NOVO CHAMADO] Equipe: {team_id} | Local: {location} | Problema: {issue}")

    # Agenda a notificacao e persistencia em segundo plano
    background_tasks.add_task(
        background_notify,
        team_id,
        issue,
        location
    )

    return JSONResponse({
        "ok": True,
        "mensagem": "Chamado registrado com sucesso. Um mentor entrara em contato em breve.",
        "team_id": team_id,
        "timestamp": formatar_data_br(datetime.now())
    })


# =============================================================================
# ROTAS DE STATUS DA EQUIPE (HTML + API)
# =============================================================================

@app.get("/team-status", response_class=HTMLResponse, tags=["Equipes"], summary="Pagina de acompanhamento de chamado")
def team_status_page(
    request: Request,
    team: int
):
    """Exibe a pagina de status para uma equipe especifica acompanhar seu chamado."""
    return templates.TemplateResponse(
        "team_status.html",
        {
            "request": request,
            "team_id": team,
            "title": f"Status da Equipe {team} - OverClocked CPFANI",
            "lang": settings.LANG
        }
    )


@app.get("/team/{team_id}/status", tags=["Equipes"], summary="API de status do chamado da equipe")
def team_status_api(
    team_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna o status do ultimo chamado registrado pela equipe.
    Utilizado para atualizacao dinamica da interface via JavaScript.
    """
    latest_query = (
        db.query(Query)
        .filter(Query.team_id == team_id)
        .order_by(desc(Query.created_at))
        .first()
    )

    if not latest_query:
        return JSONResponse(
            {"detail": "Nenhum chamado ativo encontrado para esta equipe."},
            status_code=404
        )

    mentor = (
        db.query(Mentor)
        .filter(Mentor.id == latest_query.mentor_id)
        .first()
    )

    return {
        "issue": latest_query.issue,
        "status": latest_query.status,
        "status_descricao": {
            "pending": "Aguardando atendimento",
            "in_progress": "Em atendimento",
            "resolved": "Resolvido",
            "cancelled": "Cancelado"
        }.get(latest_query.status, latest_query.status),
        "mentor": mentor.name if mentor else "Aguardando atribuicao",
        "updated_at": formatar_data_br(latest_query.created_at)
    }


# =============================================================================
# ROTAS DO DASHBOARD DE MENTORES (HTML + API)
# =============================================================================

@app.get("/mentors-dashboard", response_class=HTMLResponse, tags=["Mentores"], summary="Painel de controle de mentores")
def mentors_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Exibe o painel administrativo para mentores gerenciarem sua disponibilidade e chamados."""
    mentors = db.query(Mentor).all()

    return templates.TemplateResponse(
        "mentor_dashboard.html",
        {
            "request": request,
            "mentors": mentors,
            "title": "Painel de Mentores - OverClocked CPFANI",
            "lang": settings.LANG
        }
    )


@app.get("/mentors/state", tags=["Mentores"], summary="API de estado dos mentores")
def mentors_state(db: Session = Depends(get_db)):
    """Retorna a lista de mentores com seu estado atual para atualizacao da interface."""
    mentors = db.query(Mentor).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "is_active": m.is_active,
            "is_active_desc": "Disponivel" if m.is_active else "Indisponivel",
            "current_load": m.current_load,
            "max_load": m.max_load,
            "load_percentage": round((m.current_load / m.max_load * 100) if m.max_load > 0 else 0),
        }
        for m in mentors
    ]


@app.patch("/mentors/{mentor_id}/toggle-availability", tags=["Mentores"], summary="Alterna disponibilidade do mentor")
def toggle_mentor_availability(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    """
    Alterna o status de disponibilidade de um mentor (ativo/inativo).
    Utilizado pelo painel para que mentores gerenciem sua fila de atendimento.
    """
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not mentor:
        raise HTTPException(
            status_code=404,
            detail="Mentor nao encontrado. Verifique o identificador informado."
        )

    # Salva o estado anterior para log
    estado_anterior = "ativo" if mentor.is_active else "inativo"
    
    # Alterna o status
    mentor.is_active = not mentor.is_active
    db.commit()
    db.refresh(mentor)

    # Log interno da alteracao
    print(f"[MENTOR] {mentor.name} alterou status de {estado_anterior} para {'ativo' if mentor.is_active else 'inativo'}")

    return {
        "id": mentor.id,
        "name": mentor.name,
        "is_active": mentor.is_active,
        "is_active_desc": "Disponivel" if mentor.is_active else "Indisponivel",
        "current_load": mentor.current_load,
        "max_load": mentor.max_load,
        "mensagem": f"Status alterado para {'disponivel' if mentor.is_active else 'indisponivel'} com sucesso."
    }


# =============================================================================
# TRATAMENTO GLOBAL DE ERROS (RESPONSIVAS EM PT-BR)
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Retorna erros HTTP com mensagens em portugues para a API."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": True,
            "codigo": exc.status_code,
            "mensagem": exc.detail if isinstance(exc.detail, str) else "Ocorreu um erro na requisicao.",
            "caminho": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura erros nao previstos e retorna resposta generica em pt-BR."""
    # Log interno do erro para diagnostico (em producao, usar logger adequado)
    print(f"[ERRO NAO TRATADO] {request.method} {request.url}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "erro": True,
            "codigo": 500,
            "mensagem": settings.MESSAGES["erro_servidor"],
            "detalhe": "Erro interno processado. Contate o administrador se o problema persistir."
        }
    )