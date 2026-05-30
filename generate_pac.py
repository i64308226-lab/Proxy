import urllib.request
import json

# Рабочий адрес АнтиЗапрета
ANTIZAPRET_URL = "https://antizapret.prostovpn.org/domains-export.txt"

# Популярный и стабильный список заблокированных ООН/Meta/зарубежных сервисов из комьюнити (взамен упавшей Антицензории)
# Этот список содержит Instagram, Facebook, Twitter, OpenAI и т.д.
FOREIGN_SERVICES_URL = "https://raw.githubusercontent.com/ru-vps/web-proxy/main/domains.txt"

PAC_FILE = "antizapret.pac"
TXT_FILE = "proxy.txt"

# Сервера прокси
PROXY_ANTIZAPRET = "HTTPS proxy-ssl.antizapret.prostovpn.org:1443; DIRECT"
# В качестве резервного зарубежного прокси для Инсты временно ставим прокси Антицензории, 
# либо ты можешь вписать сюда свой личный, если он у тебя есть
PROXY_FOREIGN = "PROXY proxy.anticenz.org:3128; DIRECT"

# Строчка для твоего файла proxy.txt (для ручной настройки мобильного)
RAW_PROXY_DATA = "proxy.anticenz.org:3128"

def download_list(url, name):
    print(f"Скачивание списка {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Ошибка скачивания {name}: {e}")
        return []

# Скачиваем списки
az_domains = download_list(ANTIZAPRET_URL, "АнтиЗапрет")
foreign_domains = download_list(FOREIGN_SERVICES_URL, "Зарубежные сервисы (Инста/Meta)")

# Если основной список скачался, скрипт продолжит работу
if not az_domains:
    print("Критическая ошибка: не удалось скачать список АнтиЗапрета.")
    exit(1)

# Форматируем домены для JS
js_az = ",\n".join([f'    "{d.strip()}": 1' for d in az_domains if d.strip() and not d.startswith("#")])
js_foreign = ",\n".join([f'    "{d.strip()}": 1' for d in foreign_domains if d.strip() and not d.startswith("#")])

pac_content = f"""function FindProxyForURL(url, host) {{
    host = host.toLowerCase();
    
    var az_domains = {{
{js_az}
    }};

    var foreign_domains = {{
{js_foreign}
    }};

    var suffix = host;
    while (suffix) {{
        // Сначала проверяем Инсту и зарубежные сервисы
        if (foreign_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_FOREIGN}";
        }}
        // Затем обычный АнтиЗапрет
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

# Записываем файлы
with open(PAC_FILE, "w", encoding="utf-8") as f:
    f.write(pac_content)

with open(TXT_FILE, "w", encoding="utf-8") as f:
    f.write(RAW_PROXY_DATA)

print("Все файлы успешно обновлены и сохранены!")
