"""Создание локального пароля, который не попадает в Git и образы."""
import secrets
from pathlib import Path

target = Path(__file__).parent / '.env'
if target.exists():
    print('.env уже существует, оставлен без изменений')
else:
    target.write_text('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24) + '\nWEB_PORT=8090\n', encoding='utf-8')
    target.chmod(0o600)
    print('.env создан')
