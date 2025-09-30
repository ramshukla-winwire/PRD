# Configuration for PRD Agent - Groq Hackathon Version

## Agent Settings
AGENT_ID = "prd-agent-groq"
AGENT_NAME = "BRD Generator - Powered by Groq"
AGENT_VERSION = "2.0.0"
AGENT_PORT = 8083

## Groq API Configuration
GROQ_API_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.1-8b-instant"  # Primary model - fast and reliable
# Alternative models if primary fails:
# GROQ_MODEL = "mixtral-8x7b-32768"  # Mixtral alternative
# GROQ_MODEL = "gemma-7b-it"  # Gemma alternative
GROQ_MAX_TOKENS = 8192
GROQ_TEMPERATURE = 0.1

## CIRCLES Framework Configuration
CIRCLES_STEPS = [
    "comprehend_the_situation",
    "identify_the_customer", 
    "report_the_customers_needs",
    "cut_through_prioritization",
    "list_solutions",
    "evaluate_trade_offs",
    "summarize_recommendations"
]

## Template Configuration
PRD_TEMPLATE_FILE = "prd_template.prompt"
SYSTEM_PROMPT_FILE = "prd_system_prompt.prompt"

## Memory Configuration (Optional for hackathon)
SESSION_EXPIRY_DAYS = 7

## Performance Settings
MAX_CONCURRENT_SESSIONS = 50
DEFAULT_TIMEOUT_SECONDS = 60

## Debug and Logging
LOG_LEVEL = "INFO"
ENABLE_DEBUG_LOGGING = True

## File Paths
DATA_DIR = "data"
PROMPTS_DIR = "prompts"
UTILS_DIR = "utils"

## Hackathon Features
DEMO_MODE = True
FAST_GENERATION = True
