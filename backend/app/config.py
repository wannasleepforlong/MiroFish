"""
Configuration management.
Loads settings from the project-root `.env` file.
"""
import os
import secrets
import warnings
from dotenv import load_dotenv

# Load the project-root `.env` file.
# Path: MiroFish/.env (relative to backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # If no root `.env` exists, fall back to the process environment.
    load_dotenv(override=True)


def _load_llm_configs() -> list[dict]:
    """
    Dynamically discover all numbered LLM configs from environment variables.

    Scans for LLM_API_KEY_1, LLM_API_KEY_2, ... up to the first missing index,
    then returns a list of config dicts. An entry is included only if its
    API key is present and non-empty.

    Returns:
        list[dict]: Each dict has keys: 'api_key', 'base_url', 'model_name', 'index'.

    Example entry:
        {
            'index': 1,
            'api_key': '',
            'base_url': 'https://api.mistral.ai/v1',
            'model_name': 'mistral-small-latest',
        }
    """
    configs = []
    index = 1

    while True:
        api_key = os.environ.get(f'LLM_API_KEY_{index}', '').strip()

        # Stop scanning at the first missing key
        if not api_key:
            break

        configs.append({
            'index': index,
            'api_key': api_key,
            'base_url': os.environ.get(f'LLM_BASE_URL_{index}', 'https://api.openai.com/v1').strip(),
            'model_name': os.environ.get(f'LLM_MODEL_NAME_{index}', 'gpt-4o-mini').strip(),
        })
        index += 1

    return configs


class Config:
    """Flask configuration."""

    # ------------------------------------------------------------------ #
    #  Flask settings                                                      #
    # ------------------------------------------------------------------ #
    # SECURITY: SECRET_KEY should be set via environment variable
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        warnings.warn(
            "SECRET_KEY not set in environment variables. Using a temporary key for this session. "
            "Please set SECRET_KEY in your .env file for production use.",
            UserWarning
        )
        _secret_key = secrets.token_hex(32)
    SECRET_KEY = _secret_key

    # SECURITY: DEBUG should default to False for production safety
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Keep JSON output readable instead of forcing ASCII escapes.
    JSON_AS_ASCII = False

    # ------------------------------------------------------------------ #
    #  LLM settings — legacy single-key (kept for backwards compatibility) #
    # ------------------------------------------------------------------ #
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME')

    # ------------------------------------------------------------------ #
    #  Multi-LLM settings                                                  #
    # ------------------------------------------------------------------ #

    # List of all discovered LLM configs, in index order (_1, _2, _3, ...)
    LLM_CONFIGS: list[dict] = _load_llm_configs()

    # Total number of LLMs configured
    LLM_COUNT: int = len(LLM_CONFIGS)

    # ------------------------------------------------------------------ #
    #  Zep settings                                                        #
    # ------------------------------------------------------------------ #
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')

    # ------------------------------------------------------------------ #
    #  File upload settings                                                #
    # ------------------------------------------------------------------ #
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}

    # ------------------------------------------------------------------ #
    #  Text processing settings                                            #
    # ------------------------------------------------------------------ #
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50

    # ------------------------------------------------------------------ #
    #  OASIS simulation settings                                           #
    # ------------------------------------------------------------------ #
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')

    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]

    # ------------------------------------------------------------------ #
    #  Report agent settings                                               #
    # ------------------------------------------------------------------ #
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    # ------------------------------------------------------------------ #
    #  Misc settings                                                       #
    # ------------------------------------------------------------------ #
    LANGUAGE = os.environ.get('LANGUAGE', 'en')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_llm(cls, index: int) -> dict | None:
        """
        Retrieve a specific LLM config by its 1-based index.

        Args:
            index (int): 1-based index matching the .env suffix (e.g. 1 -> LLM_API_KEY_1).

        Returns:
            dict | None: The config dict, or None if the index is out of range.

        Example:
            cfg = Config.get_llm(2)
            # {'index': 2, 'api_key': '...', 'base_url': '...', 'model_name': '...'}
        """
        for cfg in cls.LLM_CONFIGS:
            if cfg['index'] == index:
                return cfg
        return None

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate required configuration values.

        Returns:
            list[str]: Human-readable error messages. Empty list means valid.
        """
        errors = []

        # Must have at least one LLM configured (numbered or legacy).
        if cls.LLM_COUNT == 0 and not cls.LLM_API_KEY:
            errors.append(
                "No LLM API keys configured. "
                "Add LLM_API_KEY_1 (and optionally _2, _3, ...) to your .env file."
            )

        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY is not configured.")

        return errors


# ------------------------------------------------------------------ #
#  Module-level summary (useful for startup logs)                      #
# ------------------------------------------------------------------ #

if __name__ == '__main__':
    print(f"LLMs configured: {Config.LLM_COUNT}")
    for llm in Config.LLM_CONFIGS:
        masked_key = llm['api_key'][:6] + '...' + llm['api_key'][-4:]
        print(
            f"  [{llm['index']}] model={llm['model_name']:<30s} "
            f"base_url={llm['base_url']:<35s} key={masked_key}"
        )

    errors = Config.validate()
    if errors:
        print("\nConfiguration errors:")
        for e in errors:
            print(f"  x {e}")
    else:
        print("\nConfiguration is valid.")
