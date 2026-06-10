from fastapi import APIRouter, Request, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from overclocked_helpdesk.db.session import get_db
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.utils.qr import generate_team_qr

# Router para rotas administrativas do sistema
router = APIRouter(prefix="/admin", tags=["Administracao"])
templates = Jinja2Templates(directory="templates")

QR_DIR = "static/qr"


# -------------------------
# Funções Auxiliares
# -------------------------
def qr_exists(team_id: int) -> bool:
    """Verifica se o arquivo de QR Code da equipe já existe no diretório."""
    return os.path.exists(f"{QR_DIR}/team_{team_id}.png")


# -------------------------
# Painel Administrativo
# -------------------------
@router.get("", response_class=HTMLResponse, summary="Painel administrativo principal")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Renderiza o painel administrativo com a lista de equipes (1 a 40) 
    e o status de geração de seus QR Codes, além da lista de mentores.
    """
    teams = [
        {"id": i, "qr_exists": qr_exists(i)}
        for i in range(1, 41)
    ]

    mentors = db.query(Mentor).order_by(Mentor.id.asc()).all()

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "teams": teams,
            "mentors": mentors
        }
    )


# -------------------------
# Gerar QR Code
# -------------------------
@router.post("/teams/{team_id}/generate-qr", summary="Gera QR Code para uma equipe específica")
def generate_qr(team_id: int):
    """Gera o arquivo de imagem do QR Code para a equipe informada."""
    if team_id < 1 or team_id > 40:
        raise HTTPException(status_code=400, detail="Equipe inválida. O ID deve estar entre 1 e 40.")

    path = generate_team_qr(team_id)
    return {"ok": True, "path": path}


# -------------------------
# Adicionar Mentor
# -------------------------
@router.post("/mentors", summary="Adiciona um novo mentor ao sistema")
def add_mentor(
    name: str = Form(...),
    email: str = Form(...),
    max_load: int = Form(3),
    db: Session = Depends(get_db)
):
    """Cria um novo registro de mentor com carga inicial zero e status ativo."""
    mentor = Mentor(
        name=name.strip(),
        email=email.strip(),
        max_load=max_load,
        current_load=0,
        is_active=True
    )

    db.add(mentor)
    db.commit()
    db.refresh(mentor)

    return {"ok": True, "id": mentor.id}


# -------------------------
# Atualizar Mentor
# -------------------------
@router.patch("/mentors/{mentor_id}", summary="Atualiza os dados de um mentor existente")
def update_mentor(
    mentor_id: int,
    name: str = Form(...),
    email: str = Form(...),
    max_load: int = Form(...),
    is_active: bool = Form(...),
    db: Session = Depends(get_db)
):
    """Atualiza nome, e-mail, carga máxima e status de atividade de um mentor."""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor não encontrado")

    mentor.name = name.strip()
    mentor.email = email.strip()
    mentor.max_load = max_load
    mentor.is_active = is_active

    # Garantia de segurança: ajustar carga atual se o limite máximo foi reduzido
    if mentor.current_load > mentor.max_load:
        mentor.current_load = mentor.max_load

    db.commit()
    return {"ok": True}


# -------------------------
# Excluir Mentor
# -------------------------
@router.delete("/mentors/{mentor_id}", summary="Remove um mentor do sistema")
def delete_mentor(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove um mentor do banco de dados.
    Bloqueia a exclusão se o mentor possuir chamados ativos em sua carga.
    """
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor não encontrado")

    if mentor.current_load > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um mentor com chamados ativos em sua carga"
        )

    db.delete(mentor)
    db.commit()

    return {"ok": True}