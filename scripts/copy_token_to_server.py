#!/usr/bin/env python3
"""
Script para copiar token.json de forma segura para servidor remoto

Uso:
    python scripts/copy_token_to_server.py usuario@servidor:/caminho/bot
"""

import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("❌ Erro: Especifique o destino")
        print("\nUso:")
        print("  python scripts/copy_token_to_server.py usuario@servidor:/caminho/bot")
        print("\nExemplo:")
        print(
            "  python scripts/copy_token_to_server.py root@192.168.1.100:/root/bot-youtube-pao"
        )
        sys.exit(1)

    destination = sys.argv[1]

    # Verificar se token.json existe
    token_path = Path("config/token.json")

    if not token_path.exists():
        print("❌ Erro: config/token.json não encontrado!")
        print("\n📝 Passos:")
        print("1. Execute o bot localmente primeiro: python main.py")
        print("2. Faça login no navegador")
        print("3. O token será salvo em config/token.json")
        print("4. Rode este script novamente")
        sys.exit(1)

    print("✅ Token encontrado!")
    print(f"📁 Origem: {token_path.absolute()}")
    print(f"🎯 Destino: {destination}")

    # Confirmar
    resposta = input("\n⚠️  Continuar? (s/N): ").strip().lower()

    if resposta not in ["s", "sim", "y", "yes"]:
        print("❌ Operação cancelada")
        sys.exit(0)

    # Executar SCP
    try:
        print("\n📤 Copiando token...")

        comando = ["scp", str(token_path), f"{destination}/config/token.json"]

        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)

        print("✅ Token copiado com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Conecte ao servidor via SSH")
        print("2. Verifique permissões: chmod 600 config/token.json")
        print("3. Rode o bot: python3 main.py")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao copiar: {e}")
        print(f"\n📄 Stderr: {e.stderr}")
        print("\n💡 Dicas:")
        print("- Verifique se o SSH está configurado")
        print("- Teste conexão: ssh usuario@servidor")
        print("- Verifique se o diretório existe no servidor")
        sys.exit(1)

    except FileNotFoundError:
        print("❌ Erro: Comando 'scp' não encontrado!")
        print("\n📝 Instale SCP:")
        print("  Windows: Incluído no Windows 10+ ou instale OpenSSH")
        print("  Linux/Mac: sudo apt install openssh-client")
        sys.exit(1)


if __name__ == "__main__":
    main()
