# Intent: chat-client

## Goal
A small Python command-line program that takes one question as `argv[1]`, sends it to an OpenRouter-compatible chat completions endpoint, prints the model's answer, and finishes with one final line that shows the model name plus the input and output token counts.

## Who it is for
The developer running it from a terminal. Today they would either open the OpenRouter web UI or hand-write HTTP/JSON boilerplate every time; this gives them a one-shot, scriptable call they can wire into other tools.

## Constraints
- Python, standard library only (no `pip install`, no third-party packages — `urllib` + `json` only).
- API key read from the `OPENROUTER_API_KEY` environment variable.
- Base URL read from the `CHAT_BASE_URL` environment variable.
- Model name read from the `CHAT_MODEL` environment variable.
- Nothing secret in the source code — keys and URLs live only in the environment.
- Intended model for this run: `minimax/minimax-m3`.

## Not in scope
- Streaming responses (the full reply is read before anything is printed).
- Conversation history or multi-turn dialogue.
- Retries, backoff, or any error recovery beyond a single clear failure message and a non-zero exit.
- Tool / function calling.
- Multiple questions per invocation.
- Pretty formatting, colors, or interactive prompts.

## Success looks like
1. `python chat_client.py "What is 2 + 2?"` prints `4` (or similar) and then a final line of the form `model=<name> input_tokens=<n> output_tokens=<n>`.
2. Running with any required env var unset exits non-zero and prints a message naming the missing variable; no API call is made.
3. `grep "sk-or-" chat_client.py` finds nothing — the source contains no key material (only the env var's name, never its value).

## Open questions
None — all settled in the interview.

**Approved by:** Ken Kousen, Sep 21, 2026
