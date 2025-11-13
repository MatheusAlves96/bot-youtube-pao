"""
Script minimalista para debugar batch processing
Não importa dependências do bot, apenas Google API
"""

import asyncio
import re
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Padrão ISO 8601
ISO8601_PATTERN = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

# IDs de teste
TEST_VIDEO_IDS = [
    "DelhLppPSxY",  # Gone Away
    "o_l4Ab5FRwQ",  # Wrong Side of Heaven
    "ZVUyyHYkBHk",  # Wash It All Away
]


def load_credentials():
    """Carrega credenciais do token.json"""
    token_path = Path(__file__).parent / "config" / "token.json"

    if not token_path.exists():
        print(f"❌ token.json não encontrado em: {token_path}")
        return None

    import json

    with open(token_path) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes"),
    )

    return creds


async def test_batch_minimal():
    """Teste minimalista do batch"""
    print("=" * 80)
    print("🔍 TESTE MINIMALISTA DE BATCH")
    print("=" * 80)

    # 1. Carregar credenciais
    print("\n1️⃣ Carregando credenciais...")
    creds = load_credentials()
    if not creds:
        return
    print("   ✅ Credenciais carregadas")

    # 2. Criar client YouTube
    print("\n2️⃣ Criando YouTube client...")
    youtube = build("youtube", "v3", credentials=creds)
    print("   ✅ Client criado")

    # 3. Fazer chamada batch
    print(f"\n3️⃣ Fazendo chamada batch para {len(TEST_VIDEO_IDS)} vídeos...")
    ids_str = ",".join(TEST_VIDEO_IDS)
    print(f"   IDs: {ids_str}")

    try:
        request = youtube.videos().list(part="contentDetails", id=ids_str)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, request.execute)

        print("\n4️⃣ RESPOSTA DA API:")
        items = response.get("items", [])
        print(f"   Items retornados: {len(items)}")

        if not items:
            print("   ❌ NENHUM ITEM RETORNADO!")
            print(f"   Response completo: {response}")
            return

        # 4. Processar cada item
        print("\n5️⃣ PROCESSANDO ITEMS:")
        durations = {}

        for item in items:
            vid_id = item["id"]
            duration_str = item["contentDetails"]["duration"]

            print(f"\n   📹 Vídeo: {vid_id}")
            print(f"      Duration string: {duration_str}")

            # Parsear
            match = ISO8601_PATTERN.match(duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)

                total_minutes = hours * 60 + minutes
                if seconds >= 30:
                    total_minutes += 1

                durations[vid_id] = total_minutes
                print(
                    f"      ✅ Parseado: {hours}h {minutes}m {seconds}s = {total_minutes}min"
                )
            else:
                print(f"      ❌ Falha no parsing!")
                durations[vid_id] = 0

        # 5. Resultado final
        print("\n6️⃣ RESULTADO FINAL:")
        print(f"   Dicionário durations:")
        print(f"      Tamanho: {len(durations)}")
        print(f"      Vazio: {not durations}")
        print(f"      Conteúdo: {durations}")

        # 6. Simulação do código real
        print("\n7️⃣ SIMULAÇÃO DO CÓDIGO REAL:")
        for vid_id in TEST_VIDEO_IDS:
            duration_from_dict = durations.get(vid_id, 0)
            print(f"   durations.get('{vid_id}', 0) = {duration_from_dict}")

    except Exception as e:
        print(f"\n❌ EXCEÇÃO:")
        print(f"   {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("🏁 TESTE FINALIZADO")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_batch_minimal())
