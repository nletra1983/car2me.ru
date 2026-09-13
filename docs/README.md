# Документация Car2Me

С чего начать новому человеку (или себе через месяц).

## Карта

| Что нужно | Куда |
|-----------|------|
| Как устроена система сейчас | [architecture.md](architecture.md) + [Architecture AS IS.drawio](Architecture%20AS%20IS.drawio) |
| Требования (REQ / NFR) | [requirements/](requirements/) · [NFR.md](requirements/NFR.md) |
| Смоук перед релизом | [qa/smoke-checklist.md](qa/smoke-checklist.md) |
| Как публиковать сайт | [how-i-deploy.md](how-i-deploy.md) (мой цикл) · [../DEPLOY-MANUAL.md](../DEPLOY-MANUAL.md) (подробно) |
| Лог работ (мост к ментору) | [SESSION-LOG.md](SESSION-LOG.md) |
| План дня ландшафта | [HANDOFF-landscape-day1.md](HANDOFF-landscape-day1.md) |

## Что в git / что только локально

| Зона | Примеры | В git? |
|------|---------|--------|
| **A. Публичный сайт** | `index.html`, legal, `samples/`, `CNAME`, картинки витрины | **Да** — это прод GitHub Pages |
| **B. Операционка / ПДн** | `Ответы/`, клиентские файлы в `Отчёты/`, личные PDF, исходники фото автора | **Нет** |
| **C. Система проекта** | `docs/`, `.cursor/skills`, `scripts/` без секретов | **Да** |
| **D. Маркетинг/черновики** | `content/` (посты), `ADS-QUICK-LAUNCH.md`, `drive2.html` | **Да** (без pptx и ПДн) |

Публичный пример отчёта: `samples/primer-otchyota.pdf` (не путать с рабочими `Отчёты/`).

## Репозиторий

- GitHub: https://github.com/nletra1983/car2me.ru  
- Сайт: https://car2me.ru  
