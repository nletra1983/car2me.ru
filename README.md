# Car2Me — сайт для GitHub Pages

**Домен:** car2me.ru  
**GitHub:** https://github.com/nletra1983/car2me.ru

## Обновление сайта

```powershell
git add .
git commit -m "Update content"
git push
```

Изменения на сайте через 1–2 минуты.

## DNS на reg.ru

Убедитесь: DNS-серверы `ns1.reg.ru`, `ns2.reg.ru`. Удалите парковочные A-записи.

| Тип | Subdomain | Значение |
|-----|-----------|----------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | nletra1983.github.io |

Подробная инструкция: [DEPLOY-MANUAL.md](DEPLOY-MANUAL.md)
