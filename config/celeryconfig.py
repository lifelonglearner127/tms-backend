from celery.schedules import crontab


broker_url = 'amqp://localhost'

beat_schedule = {
    'update_monthly_report': {
        'task': 'tms.order.tasks.update_monthly_report',
        'schedule': crontab(0, 0, day_of_month='3'),
    },
}

# task_always_eager = True
