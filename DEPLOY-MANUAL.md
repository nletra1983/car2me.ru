# Инструкция: публикация car2me.ru

> Хостинг: **GitHub Pages** (без VPS, без nginx, без certbot).
> SSL включается в GitHub после настройки DNS — не ищите отдельный сертификат.

---

## Часть 1. Репозиторий на GitHub (вручную)

### 1.1 Создать репозиторий

1. Откройте https://github.com/new
2. **Repository name:** `car2me.ru`
3. **Public** — обязательно для бесплатного GitHub Pages
4. **Не** ставьте галочки «Add README», «Add .gitignore», «Choose a license» — репозиторий должен быть пустым
5. Нажмите **Create repository**

### 1.2 Загрузить код

В папке проекта в PowerShell:

```powershell
cd D:\Cursor\car2me-site
git init
git add .
git commit -m "Initial commit: static site"
git branch -M main
git remote add origin https://github.com/nletra1983/car2me.ru.git
git push -u origin main
```

**Важно:**
- Сообщения коммитов — **на английском** (на Windows кириллица в `git log` может отображаться кракозябрами)
- В PowerShell команды через `;`, не через `&&`
- Если `git push` просит логин — используйте Personal Access Token вместо пароля (GitHub → Settings → Developer settings → Personal access tokens)

### 1.3 Проверить файл CNAME

В корне репозитория на GitHub должен быть файл `CNAME` с одной строкой:

```
car2me.ru
```

Без `https://`, без `/`, без `www`.

---

## Часть 2. GitHub Pages (вручную)

1. Откройте https://github.com/nletra1983/car2me.ru → **Settings** → слева **Pages**
2. **Build and deployment → Source:** Deploy from a branch
3. **Branch:** `main` → папка **`/ (root)`** → **Save**
4. Подождите 1–2 мин — появится URL вида `https://nletra1983.github.io/car2me.ru/`
5. **Custom domain:** введите `car2me.ru` → **Save**
6. GitHub может показать ⚠️ DNS check failed — **это нормально**, пока не настроен reg.ru. Не отменяйте домен.

### HTTPS (позже, после DNS)

1. Подождите **15–60 минут** после настройки DNS на reg.ru
2. Вернитесь в **Settings → Pages**
3. Нажмите **Check again** рядом с custom domain
4. Когда DNS подтверждён — включите **Enforce HTTPS**

⚠️ **Не паникуйте**, если галочка HTTPS серая сразу — так и должно быть до пропагации DNS.

---

## Часть 3. DNS на reg.ru (вручную)

1. https://www.reg.ru/ → **Мои домены** → клик по `car2me.ru`
2. **DNS-серверы и управление зоной**
3. Убедитесь, что DNS-серверы: **`ns1.reg.ru`** и **`ns2.reg.ru`**
4. Откройте **Ресурсные записи**
5. **Удалите парковочные записи** (A-запись `@` на IP reg.ru / парковку) — они мешают GitHub
6. **Добавьте 4 отдельные A-записи** (каждый IP — новая запись):

| Тип | Subdomain | Значение |
|-----|-----------|----------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

7. **Добавьте CNAME** для www:

| Тип | Subdomain | Значение |
|-----|-----------|----------|
| CNAME | www | nletra1983.github.io |

⚠️ В CNAME указывайте **`nletra1983.github.io`**, не `nletra1983.github.io/car2me.ru`.

8. Сохраните. Подождите **15–60 минут**.

---

## Часть 4. Проверка

### На reg.ru / после ожидания

1. GitHub → Settings → Pages → **Check again** → включить **Enforce HTTPS**
2. Откройте https://car2me.ru в браузере

### Команды (PowerShell)

```powershell
Invoke-WebRequest -Uri "https://car2me.ru" -Method Head -UseBasicParsing
# Ожидается: StatusCode 200

nslookup car2me.ru 8.8.8.8
# Ожидается: четыре IP 185.199.108–111.153
```

---

## Частые ошибки

| Симптом | Что делать |
|---------|------------|
| HTTPS нельзя включить | Подождать DNS, нажать Check again — не включать certbot и не покупать SSL |
| Открывается страница reg.ru «домен не подключён» | Удалить парковочные A-записи, добавить 4 A на GitHub IP |
| `InvalidDNSError` в GitHub | Проверить записи, подождать до 24 ч, Check again |
| Работает www, не работает без www | Добавить все 4 A-записи для `@` |
| Сайт открывается через VPN, но не дома | Локальный DNS провайдера; проверить `nslookup car2me.ru 8.8.8.8` |
| Думали, нужен Netlify / VPS | Для статического сайта достаточно GitHub Pages |

---

## Дальнейшие обновления сайта

После правок в Cursor:

```powershell
cd D:\Cursor\car2me-site
git add .
git commit -m "Update content"
git push
```

Сайт обновится за 1–2 минуты.

---

**Когда выполните части 1–3 — напишите, проверим HTTPS и DNS вместе.**
