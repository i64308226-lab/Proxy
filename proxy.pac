function FindProxyForURL(url, host) {
    // 1. Исключаем локальную сеть и домашний роутер
    if (isPlainHostName(host) || shExpMatch(host, "*.local")) {
        return "DIRECT";
    }

    // 2. Делаем быстрый DNS-запрос. Если сайт заблокирован в РФ,
    // система АнтиЗапрета подменит IP, и этот фильтр сработает абсолютно на ЛЮБОЙ заблокированный сайт.
    if (!isInNet(dnsResolve(host), "0.0.0.0", "255.255.255.255")) {
        // Направляем весь заблокированный трафик на рабочие сервера АнтиЗапрета
        return "PROXY proxy.antizapret.prostovpn.org:3128; PROXY p.thenewone.lol:3128; DIRECT";
    }

    // Все разрешенные сайты открываем напрямую на полной скорости
    return "DIRECT";
}
