#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_manager.settings')

if __name__ == '__main__':
    env_path = './.env'

    load_dotenv(dotenv_path=env_path)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    is_testing = 'test' in sys.argv
    # https://github.com/jazzband/django-nose/issues/180#issuecomment-93371418
    if is_testing:
        import coverage
        cov = coverage.coverage(source=["content_manager", "messenger_users", "posts", "random_codes"])
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()
        cov.report()
