import urllib.request

ANTIZAPRET_URL = "https://antizapret.prostovpn.org/domains-export.txt"
ANTICENZ_URL = "https://anticenz.org/export/domains.txt"

# Имена двух разных файлов
PAC_FILE = "antizapret.pac"
TXT_FILE = "proxy.txt"

# Адреса серверов
PROXY_ANTIZAPRET = "HTTPS proxy-ssl.antizapret.prostovpn.org:1443; DIRECT"
PROXY_ANTICENZ = "PROXY proxy.anticenz.org:3128; DIRECT"

# Чистый адрес прокси Антицензории для мобильного (без лишнего мусора)
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

az_domains = download_list(ANTIZAPRET_URL, "АнтиЗапрет")
ac_domains = download_list(ANTICENZ_URL, "Антицензория")

if not az_domains and not ac_domains:
    print("Ошибка загрузки списков.")
    exit(1)

js_az = ",\n".join([f'    "{d.strip()}": 1' for d in az_domains if d.strip()])
js_ac = ",\n".join([f'    "{d.strip()}": 1' for d in ac_domains if d.strip()])

# 1. Генерация УМНОГО PAC-файла
pac_content = f"""function FindProxyForURL(url, host) {{
    host = host.toLowerCase();
    
    var az_domains = {{
{js_az}
    }};

    var ac_domains = {{
{js_ac}
    }};

    var suffix = host;
    while (suffix) {{
        if (ac_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_ANTICENZ}";
        }}
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

with open(PAC_FILE, "w", encoding="utf-8") as f:
    f.write(pac_content)

# 2. Генерация ОБЫЧНОГО текстового файла с прокси
with open(TXT_FILE, "w", encoding="utf-8") as f:
    f.write(RAW_PROXY_DATA)

print("Оба файла успешно созданы!")
