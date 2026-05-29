import urllib.request

LIST_URL = "https://antizapret.prostovpn.org:8443/domains-export.txt"
OUTPUT_FILE = "antizapret.pac"
PROXY_SERVER = "PROXY proxy.antizapret.prostovpn.org:3128; DIRECT"

print("Скачивание списка доменов...")
try:
    with urllib.request.urlopen(LIST_URL) as response:
        domains = response.read().decode('utf-8').splitlines()
except Exception as e:
    print(f"Ошибка скачивания: {e}")
    exit(1)

print(f"Загружено {len(domains)} доменов. Сборка PAC-файла...")

js_domains = ",\n".join([f'    "{domain.strip()}": 1' for domain in domains if domain.strip()])

pac_content = f"""function FindProxyForURL(url, host) {{
    host = host.toLowerCase();
    
    var blocked_domains = {{
{js_domains}
    }};

    var suffix = host;
    while (suffix) {{
        if (blocked_domains.hasOwnProperty(suffix)) {{
            return "{PROXY_SERVER}";
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

print("Файл успешно сгенерирован!")
