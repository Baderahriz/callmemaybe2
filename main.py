from llm_sdk import Small_LLM_Model

small_llm = Small_LLM_Model()


mkdir -p /goinfre/bahriz/uv-cache
mkdir -p /goinfre/bahriz/venvs

export UV_CACHE_DIR=/goinfre/bahriz/uv-cache
export UV_PROJECT_ENVIRONMENT=/goinfre/bahriz/venvs/callmemaybe
export UV_LINK_MODE=copy

uv add ./llm_sdk