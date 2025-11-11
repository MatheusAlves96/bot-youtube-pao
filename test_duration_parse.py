import re

# Padrão do código
ISO8601_DURATION_PATTERN = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

# Exemplos de durações
test_cases = [
    "PT3M45S",      # 3min 45s
    "PT4M10S",      # 4min 10s
    "PT5M55S",      # 5min 55s
    "PT10M0S",      # 10min
    "PT1H2M3S",     # 1h 2min 3s
    "PT45S",        # 45s
    "PT0M0S",       # 0s
]

print("Testando conversão ISO 8601:\n")

for duration_str in test_cases:
    match = ISO8601_DURATION_PATTERN.match(duration_str)
    
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        total_minutes = hours * 60 + minutes
        if seconds >= 30:
            total_minutes += 1
        
        print(f"✅ {duration_str:15} → {hours}h {minutes}m {seconds}s = {total_minutes} min")
    else:
        print(f"❌ {duration_str:15} → FALHOU NO PARSE")

print("\n" + "="*50)
print("Se todos passaram, o regex está correto!")
print("O problema pode ser:")
print("1. Bot não foi reiniciado após mudanças")
print("2. API do YouTube não está retornando durações")
print("3. Código antigo ainda em cache")
