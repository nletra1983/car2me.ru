# Car2Me — чеклист донастройки (01.09.2026)

Отметь по мере выполнения.

## Сайт и GitHub

- [ ] GitHub → Settings → Pages → **Check again** у custom domain
- [ ] Включить **Enforce HTTPS** (если галочка доступна)
- [ ] Открыть https://car2me.ru — лендинг грузится
- [ ] `git push` — на GitHub ещё старая версия (нет metrika, legal, обновлённого index)

```powershell
cd D:\car2me-site
git add index.html metrika.js legal.css privacy.html offer.html pd-consent.html README.md DEPLOY-MANUAL.md qr-pay.jpg
git commit -m "Add legal pages, Metrika, cookie banner"
git push
```

## Яндекс.Метрика

- [ ] Счётчик 112130182 — цели: `cta_order`, `section_order`, `pay_sber`, `cta_form`, `section_form`, `cta_case`
- [ ] После push — на сайте баннер cookie, в Метрике идут визиты

## Почта hello@car2me.ru

- [ ] DNS: MX, A `mail`, SPF, DKIM (`dkim._domainkey`), DMARC (`_dmarc`)
- [ ] Проверка: `nslookup -type=TXT dkim._domainkey.car2me.ru 8.8.8.8`
- [ ] Входящее: письмо с личной почты на hello@
- [ ] Исходящее: ответ с hello@ (mail-tester.com — цель 8+/10)
- [ ] SSL для почты в панели хостинга — включить, если ещё нет

## Юридическое

- [ ] Уведомление в РКН (pd.rkn.gov.ru) — если ещё не отправлено
- [ ] Яндекс.Форма: чекбокс согласия на ПДн

## Реклама (когда сайт на https)

- [ ] РСЯ — 3×3000 ₽, заявка = оплата
