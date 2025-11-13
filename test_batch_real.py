"""
Script de debug para testar get_videos_duration_batch() isoladamente
Usa as mesmas credenciais e configurações do bot
"""

import asyncio
import sys
import os
import re
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.youtube_service import YouTubeService
from core.logger import setup_logger

# Setup básico
logger = setup_logger("test_batch")

# IDs de vídeos conhecidos (Five Finger Death Punch - durações conhecidas)
TEST_VIDEO_IDS = [
    "DelhLppPSxY",  # Gone Away (4:30)
    "o_l4Ab5FRwQ",  # Wrong Side of Heaven (5:19)
    "ZVUyyHYkBHk",  # Wash It All Away (4:10)
    "FI5GFB5vFfM",  # Remember Everything (5:03)
    "Pn-6eOxnEMI",  # Bad Company (4:30)
]


async def test_batch():
    """Testa a função batch com vídeos reais"""
    print("=" * 80)
    print("🔍 TESTE DE BATCH PROCESSING")
    print("=" * 80)

    # Inicializar serviço
    print("\n1️⃣ Inicializando YouTubeService...")
    youtube_service = YouTubeService()
    await youtube_service.initialize()
    print("   ✅ YouTubeService inicializado")

    # Testar se youtube client está disponível
    if not youtube_service.youtube:
        print("   ❌ ERRO: youtube client não inicializado!")
        return
    print(f"   ✅ YouTube client disponível: {type(youtube_service.youtube)}")

    # Chamar método batch
    print(
        f"\n2️⃣ Chamando get_videos_duration_batch() com {len(TEST_VIDEO_IDS)} vídeos..."
    )
    print(f"   IDs: {TEST_VIDEO_IDS}")

    try:
        durations = await youtube_service.get_videos_duration_batch(TEST_VIDEO_IDS)

        print(f"\n3️⃣ RESULTADO:")
        print(f"   Tipo retornado: {type(durations)}")
        print(f"   Tamanho do dict: {len(durations)}")
        print(f"   Vazio? {not durations}")

        if durations:
            print(f"\n4️⃣ CONTEÚDO DO DICIONÁRIO:")
            for vid_id, duration in durations.items():
                print(f"   {vid_id}: {duration} minutos")
        else:
            print("\n4️⃣ ❌ DICIONÁRIO VAZIO!")
            print("   Investigando o método get_videos_duration_batch()...")

            # Debug manual: fazer chamada direta
            print("\n5️⃣ TESTE DIRETO DA API:")
            ids_str = ",".join(TEST_VIDEO_IDS)
            request = youtube_service.youtube.videos().list(
                part="contentDetails", id=ids_str
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, request.execute)

            items = response.get("items", [])
            print(f"   API retornou {len(items)} items")

            if items:
                print("\n6️⃣ PRIMEIRO ITEM DA RESPOSTA:")
                first = items[0]
                print(f"   ID: {first.get('id')}")
                print(f"   Duration: {first.get('contentDetails', {}).get('duration')}")
                print(f"   Estrutura completa:")
                import json

                print(json.dumps(first, indent=2))

                # Testar parsing
                print("\n7️⃣ TESTANDO PARSING:")
                duration_str = first["contentDetails"]["duration"]

                ISO8601_PATTERN = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
                match = ISO8601_PATTERN.match(duration_str)

                if match:
                    hours = int(match.group(1) or 0)
                    minutes = int(match.group(2) or 0)
                    seconds = int(match.group(3) or 0)
                    total_minutes = hours * 60 + minutes
                    if seconds >= 30:
                        total_minutes += 1

                    print(
                        f"   ✅ Parsing OK: {duration_str} → {hours}h {minutes}m {seconds}s = {total_minutes}min"
                    )
                else:
                    print(f"   ❌ Parsing FALHOU: {duration_str}")
            else:
                print("   ❌ API não retornou items!")
                print(f"   Response completo: {response}")

    except Exception as e:
        print(f"\n❌ EXCEÇÃO CAPTURADA:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        import traceback

        print(f"\n   Traceback:")
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("🏁 TESTE FINALIZADO")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_batch())
