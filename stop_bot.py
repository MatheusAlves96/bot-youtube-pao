"""
Script auxiliar para forçar encerramento do bot
Use este script se Ctrl+C não funcionar
"""

import os
import signal
import sys
import psutil


def stop_bot():
    """Encontra e encerra o processo do bot"""
    current_pid = os.getpid()
    bot_found = False

    print("🔍 Procurando processos do bot...")

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Verificar se é um processo Python executando main.py
            if proc.info["name"] in ["python.exe", "python", "pythonw.exe"]:
                cmdline = proc.info["cmdline"]
                if cmdline and any("main.py" in cmd for cmd in cmdline):
                    if proc.info["pid"] != current_pid:
                        print(f"✅ Bot encontrado (PID: {proc.info['pid']})")
                        print(f"   Comando: {' '.join(cmdline)}")
                        print(f"🛑 Encerrando processo...")

                        # Tentar encerrar graciosamente primeiro
                        proc.send_signal(
                            signal.SIGTERM
                            if sys.platform != "win32"
                            else signal.CTRL_C_EVENT
                        )
                        proc.wait(timeout=5)

                        if proc.is_running():
                            # Se ainda estiver rodando, forçar encerramento
                            print("⚠️  Processo não respondeu, forçando encerramento...")
                            proc.kill()

                        print("✅ Bot encerrado com sucesso!")
                        bot_found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            continue

    if not bot_found:
        print("❌ Nenhum processo do bot encontrado em execução")


if __name__ == "__main__":
    print("=" * 50)
    print("🛑 Script de Encerramento do Bot")
    print("=" * 50)

    try:
        stop_bot()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
