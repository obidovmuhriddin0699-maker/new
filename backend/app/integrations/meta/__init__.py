"""Meta (Instagram) integration."""

from app.core.logging import install_secret_filters

# Meta takes tokens as query parameters; HTTP client logs must never show them, even in
# processes that do not call configure_logging (e.g. the Celery worker).
install_secret_filters()
