# Car2Me — сайт для GitHub Pages

**Домен:** car2me.ru  
**GitHub:** https://github.com/nletra1983/car2me.ru

## Яндекс.Метрика (воронка)

1. Создайте счётчик на https://metrika.yandex.ru для `car2me.ru`
2. В `metrika.js` подставьте номер в `METRIKA_ID`
3. В Метрике → **Цели** → «JavaScript-событие», идентификаторы:
   - `cta_order` — клик «Заказать»
   - `section_order` — доскроллил до оплаты
   - `pay_sber` — клик «Сбербанк»
   - `cta_form` — «Я оплатил — форма»
   - `section_form` — доскроллил до формы
   - `cta_case` — «Читать кейс»
4. Включите **Вебвизор** и **Карту кликов** в настройках счётчика


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
