import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Создаем экземпляр Celery
app = Celery('core')

# Загружаем настройки из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи в приложениях
app.autodiscover_tasks()

# Периодические задачи (опционально)
app.conf.beat_schedule = {
    'cleanup-old-results-every-day': {
        'task': 'accounts.tasks.cleanup_old_task_results',
        'schedule': crontab(hour=3, minute=0),  # Каждый день в 3:00
    },
    'send-daily-stats': {
        'task': 'accounts.tasks.send_daily_stats',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')