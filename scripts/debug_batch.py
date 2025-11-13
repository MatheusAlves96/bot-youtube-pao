"""
Script de Debug: Batch Processing da API do YouTube
Testa a busca de durações em batch para identificar o problema
"""

import asyncio
import re
from pathlib import Path
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Padrão ISO 8601
ISO8601_DURATION_PATTERN = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def get_youtube_service():
    """Autentica e retorna serviço do YouTube"""
    creds = None
    token_path = Path("config/token.json")
    credentials_path = Path("config/credentials.json")

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def parse_duration(duration_str: str) -> int:
    """Parseia duração ISO 8601 para minutos"""
    match = ISO8601_DURATION_PATTERN.match(duration_str)

    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        total_minutes = hours * 60 + minutes
        if seconds >= 30:
            total_minutes += 1

        return total_minutes
    else:
        return 0


async def test_batch_api():
    """Testa a API de batch processing"""
    print("=" * 80)
    print("🔍 DEBUG: Batch Processing da API do YouTube")
    print("=" * 80)

    # IDs de vídeos conhecidos do Five Finger Death Punch
    test_video_ids = [
        "DelhLppPSxY",  # Gone Away
        "o_l4Ab5FRwM",  # Wrong Side Of Heaven
        "bbd1FHV7HhA",  # Bad Company
        "w5U-YT-mRmI",  # Wash It All Away
        "e8hzBQP_l-8",  # Under And Over It
    ]

    print(f"\n📋 Testando com {len(test_video_ids)} vídeos conhecidos:")
    for vid_id in test_video_ids:
        print(f"   - {vid_id}")

    try:
        youtube = get_youtube_service()

        # Fazer chamada batch
        ids_str = ",".join(test_video_ids)
        print(f"\n📡 Fazendo chamada batch para API...")
        print(f"   IDs: {ids_str}")

        request = youtube.videos().list(part="contentDetails", id=ids_str)
        response = request.execute()

        print(f"\n✅ Resposta recebida!")
        print(f"   Total de items: {len(response.get('items', []))}")

        # Verificar se retornou todos os IDs
        returned_ids = [item["id"] for item in response.get("items", [])]
        missing_ids = set(test_video_ids) - set(returned_ids)

        if missing_ids:
            print(f"\n⚠️ ATENÇÃO: {len(missing_ids)} IDs não retornados:")
            for vid_id in missing_ids:
                print(f"   - {vid_id}")

        print("\n" + "=" * 80)
        print("📊 RESULTADOS:")
        print("=" * 80)

        durations = {}
        for item in response.get("items", []):
            vid_id = item["id"]
            duration_str = item["contentDetails"]["duration"]

            # Parsear duração
            duration_minutes = parse_duration(duration_str)
            durations[vid_id] = duration_minutes

            print(f"\n🎵 Vídeo: {vid_id}")
            print(f"   📝 Duração ISO 8601: {duration_str}")
            print(f"   ⏱️  Duração parseada: {duration_minutes} minutos")

            # Validar parsing
            if duration_minutes == 0:
                print(f"   ❌ PROBLEMA: Duração é 0min!")
                match = ISO8601_DURATION_PATTERN.match(duration_str)
                if match:
                    print(f"   🔍 Grupos regex: {match.groups()}")
                else:
                    print(f"   ❌ Regex não deu match!")

        print("\n" + "=" * 80)
        print("📈 RESUMO:")
        print("=" * 80)
        print(f"   Solicitados: {len(test_video_ids)} vídeos")
        print(f"   Retornados: {len(durations)} vídeos")
        print(
            f"   Com duração válida (>0): {sum(1 for d in durations.values() if d > 0)}"
        )
        print(f"   Com duração 0: {sum(1 for d in durations.values() if d == 0)}")

        if all(d > 0 for d in durations.values()):
            print("\n✅ SUCESSO: Batch processing está funcionando corretamente!")
        else:
            print("\n❌ PROBLEMA: Alguns vídeos retornaram duração 0")

        return durations

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return {}


if __name__ == "__main__":
    print("\n🚀 Iniciando teste de batch processing...\n")
    asyncio.run(test_batch_api())
    print("\n✅ Teste concluído!")
