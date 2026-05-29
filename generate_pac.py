import urllib.request

# Ссылки на списки доменов
ANTIZAPRET_URL = "https://antizapret.prostovpn.org/domains-export.txt"
ANTICENZ_URL = "https://anticenz.org/export/domains.txt"

# Итоговый файл
OUTPUT_FILE = "antizapret.pac"

# Прокси-серверы
PROXY_ANTIZAPRET = "HTTPS proxy-ssl.antizapret.prostovpn.org:1443; DIRECT"
PROXY_ANTICENZ = "PROXY proxy.anticenz.org:3128; DIRECT"

def download_list(url, name):
    print(f"Скачивание списка {name}...")
    try:
        # Добавляем User-Agent, чтобы сервера не блокировали скрипт
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Ошибка скачивания {name}: {e}")
        return []

# Качаем оба списка
az_domains = download_list(ANTIZAPRET_URL, "АнтиЗапрет")
ac_domains = download_list(ANTICENZ_URL, "Антицензория")

if not az_domains and not ac_domains:
    print("Не удалось скачать ни один список. Выход.")
    exit(1)

# Форматируем домены для JavaScript-словерей (удаляем пустые строки и пробелы)
js_az = ",\n".join([f'    "{d.strip()}": 1' for d in az_domains if d.strip()])
js_ac = ",\n".join([f'    "{d.strip()}": 1' for d in ac_domains if d.strip()])

# Собираем комбо-PAC-файл
pac_content = f"""function FindProxyForURL(url, host) {{
    host = host.toLowerCase();
    
    // 1. База АнтиЗапрета (РФ-блокировки)
    var az_domains = {{
{js_az}
    }};

    // 2. База Антицензории (Санкции + Инстаграм/Meta)
    var ac_domains = {{
{js_ac}
    }};

    var suffix = host;
    while (suffix) {{
        // Проверяем сначала Антицензорию (Инста, ChatGPT и т.д.)
        if (ac_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_ANTICENZ}";
        }}
        // Проверяем АнтиЗапрет (Рутрекер, Флибуста и т.д.)
        if (az_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_ANTIZAPRET}";
        }}
        
        var pos = suffix.indexOf('.');
        if (pos <= 0) break;
        suffix = suffix.substring(pos + 1);
    }}

    return "DIRECT";
}}
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(pac_content)

print(f"Успешно создано! Файл {OUTPUT_FILE} содержит {len(az_domains)} доменов АЗ и {len(ac_domains)} доменов АЦ.")
