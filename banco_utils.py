"""Publicação de índices versionados sem apagar a base ativa."""
from pathlib import Path
import json
import os
import shutil
import tempfile
import uuid


def caminho_banco(raiz="./chroma_db"):
    raiz = Path(raiz)
    manifesto = raiz / "ativo.json"
    if not manifesto.exists():
        return raiz  # Compatibilidade com bancos criados pela versão anterior.
    dados = json.loads(manifesto.read_text(encoding="utf-8"))
    versao = dados["versao"]
    if not isinstance(versao, str) or not versao or any(c not in "0123456789abcdef" for c in versao):
        raise ValueError("Versão inválida no manifesto da base.")
    return raiz / "versoes" / versao


def publicar_banco(construir, raiz="./chroma_db"):
    """Só publica a nova versão quando construir() retorna após sua validação."""
    raiz = Path(raiz)
    versao = uuid.uuid4().hex
    destino = raiz / "versoes" / versao
    destino.mkdir(parents=True)
    temporario = None
    try:
        construir(destino)
        fd, temporario = tempfile.mkstemp(prefix=".ativo-", dir=raiz)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"versao": versao}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, raiz / "ativo.json")
        return destino
    except Exception:
        shutil.rmtree(destino, ignore_errors=True)
        raise
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)
