import urllib.request

# Рабочий адрес АнтиЗапрета
ANTIZAPRET_URL = "https://antizapret.prostovpn.org/domains-export.txt"

# Популярный и стабильный список зарубежных сервисов (Инстаграм, OpenAI, Твиттер и др.)
FOREIGN_SERVICES_URL = "https://raw.githubusercontent.com/ru-vps/web-proxy/main/domains.txt"

# Имена генерируемых файлов
PAC_FILE = "antizapret.pac"
TXT_FILE = "proxy.txt"

# Настройки прокси-серверов внутри PAC-файла
PROXY_ANTIZAPRET = "HTTPS proxy-ssl.antizapret.prostovpn.org:1443; DIRECT"
PROXY_FOREIGN = "PROXY proxy.anticenz.org:3128; DIRECT"

# Твой рабочий MTProto-прокси для Телеграма, который запишется в proxy.txt
TG_PROXY_LINK = "tg://proxy?server=mtproto-nl.alivevpn.com&port=443&secret=eeee676f6f676c65617069732e636f6dad64726976652e676f6f676c652e636f6d"

def download_list(url, name):
    print(f"Скачивание списка {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Ошибка скачивания {name}: {e}")
        return []

# Скачиваем списки доменов
az_domains = download_list(ANTIZAPRET_URL, "АнтиЗапрет")
foreign_domains = download_list(FOREIGN_SERVICES_URL, "Зарубежные сервисы")

if not az_domains:
    print("Критическая ошибка: не удалось скачать основной список АнтиЗапрета.")
    exit(1)

# Форматируем домены в JS-формат, отсекая пустые строки и комментарии
js_az = ",\n".join([f'    "{d.strip()}": 1' for d in az_domains if d.strip() and not d.startswith("#")])
js_foreign = ",\n".join([f'    "{d.strip()}": 1' for d in foreign_domains if d.strip() and not d.startswith("#")])

# Собираем структуру PAC-файла
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
        // Сначала проверяем Инстаграм и зарубежные сайты
        if (foreign_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_FOREIGN}";
        }}
        // Затем проверяем обычный АнтиЗапрет (Рутрекер, Флибуста и т.д.)
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

# Записываем готовый PAC-файл
with open(PAC_FILE, "w", encoding="utf-8") as f:
    f.write(pac_content)

# Записываем ссылку на прокси для Телеграма в proxy.txt
with open(TXT_FILE, "w", encoding="utf-8") as f:
    f.write(TG_PROXY_LINK)

print("Все файлы проекта успешно обновлены!")
