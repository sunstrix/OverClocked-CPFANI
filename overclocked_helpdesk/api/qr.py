from fastapi import APIRouter
from overclocked_helpdesk.utils.qr import generate_team_qr

# Router para geracao de codigos QR das equipes
router = APIRouter(prefix="/qr", tags=["QR Code"])


@router.get("/team/{team_id}", summary="Gera QR Code para uma equipe especifica")
def get_team_qr(team_id: int):
    """
    Gera e retorna o caminho do codigo QR para uma equipe especifica.
    Este QR Code pode ser escaneado para preencher automaticamente o formulario de chamado.
    
    Args:
        team_id (int): Identificador numerico da equipe.
        
    Returns:
        dict: Dicionario contendo o ID da equipe e a URL/caminho do QR Code gerado.
    """
    caminho_qr = generate_team_qr(team_id)
    
    # Mantemos as chaves 'team_id' e 'qr_url' para garantir compatibilidade 
    # com qualquer frontend ou sistema externo que ja consuma esta API.
    return {
        "team_id": team_id,
        "qr_url": caminho_qr
    }