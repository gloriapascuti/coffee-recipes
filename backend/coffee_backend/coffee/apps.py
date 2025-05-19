# import os
# from django.apps import AppConfig
#
# class CoffeeConfig(AppConfig):
#     name = 'coffee'
#
#     def ready(self):
#         # Only start in the real runserver child process (not in migrate,
#         # not in the autoreloader parent)
#         if os.environ.get('RUN_MAIN') == 'true':
#             from .generator import start_coffee_thread
#             start_coffee_thread()


import os
from django.apps import AppConfig

class CoffeeConfig(AppConfig):
    name = 'coffee'

    def ready(self):
        # Import signals so that Django registers them
        import coffee.signals  # noqa: F401

        if os.environ.get('RUN_MAIN') == 'true':
            from .generator import start_coffee_thread
            start_coffee_thread()


