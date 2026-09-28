# Spec

<!-- The agent writes this from the approved intent. You validate it against the intent.
     If the spec and the intent disagree, the intent wins until you change the intent. -->

## Intent
Implements `intent/chat-client.md`: a scriptable command-line interface to an OpenRouter-compatible chat completions API.

## Components

### ChatClient

- **What it does:** Reads a single question from the command line, sends it to a chat completions API via environment-configured credentials, and prints the response followed by a summary line with model name and token usage.

- **Language:** Python. **Why:** The intent specifies Python with standard library only. Alternative considered: Java. Java's standard library covers the HTTP side (`java.net.http.HttpClient`) and needs no build tool, but it has no JSON parser, so parsing the response would mean hand-written parsing or a third-party library, which the standard-library-only constraint rules out. Python's standard library includes `json`.

- **Model:** `minimax/minimax-m3`. **Why:** Specified in the intent as the intended model for this run. **Compared against:** `anthropic/claude-sonnet-5`, using this program, question "In one sentence, what is a context window?", one run each on 2026-09-28:

  | Model | Input tokens | Output tokens | Time | Result |
  |---|---|---|---|---|
  | `minimax/minimax-m3` | 186 | 54 | 1.2 s | Correct, one sentence |
  | `anthropic/claude-sonnet-5` | 18 | 48 | 2.6 s | Correct, one sentence, slightly fuller |

  Both answers were correct. Estimated from list prices, Sonnet 5 cost about $0.00052 and M3 about $0.0001, roughly 4–5 times less. M3 reported ten times as many input tokens for the identical request (the same pattern appeared in Week 2: 187 vs. 28); cause not verified. One question and one run each: an observation, not a benchmark. For a one-shot question tool, the cheap model was adequate here. Check actual charges on the OpenRouter Activity page.

- **Interfaces:**
  - **Input:** Command-line argument `sys.argv[1]` (the question)
  - **Environment variables:** `OPENROUTER_API_KEY`, `CHAT_BASE_URL` (includes the API version path, e.g. `https://openrouter.ai/api/v1`), `CHAT_MODEL`
  - **Output:** stdout (response text, then summary line); stderr (error messages)
  - **HTTP endpoint:** POST to `{CHAT_BASE_URL with any trailing "/" removed}/chat/completions`
  - **Exit code:** 0 on success, non-zero on any error

- **Dependencies:** Standard library only (`urllib.request`, `json`, `sys`, `os`)

## Behavior

1. Read the question from `sys.argv[1]`; exit non-zero if it is missing or if more than one argument is provided. *(The more-than-one-argument rule is added in the spec, not in the intent. It catches an unquoted question such as `python chat_client.py What is 2 + 2?`.)*
2. Validate that all three environment variables (`OPENROUTER_API_KEY`, `CHAT_BASE_URL`, `CHAT_MODEL`) are set and non-empty; if any is missing, exit non-zero with a message naming the missing variable, and make no API call.
3. Construct an HTTP POST request with a JSON payload containing the question as a single user message and `CHAT_MODEL` as the model.
4. Add an `Authorization: Bearer {OPENROUTER_API_KEY}` header and a `Content-Type: application/json` header.
5. Send the request to `{CHAT_BASE_URL}/chat/completions`, stripping any trailing `/` from `CHAT_BASE_URL` first so the URL never contains `//`. Use a 30-second timeout.
6. Parse the JSON response and read the answer from `choices[0].message.content`.
7. Read `usage.prompt_tokens`, `usage.completion_tokens`, and the top-level `model` field from the response.
8. Print the answer text to stdout.
9. Print a final line to stdout in the format `model=<model> input_tokens=<prompt_tokens> output_tokens=<completion_tokens>`, where `<model>` is the response's `model` field (the model that actually served the request, which may differ from `CHAT_MODEL`).
10. Exit with code 0 on success.
11. The source file contains no key material: `grep "sk-or-" chat_client.py` finds nothing. The key is referenced only by its environment variable name.

## Failure handling

All error messages go to **stderr**, and every failure exits non-zero. stdout carries only the answer and the summary line.

- **Missing command-line argument or more than one argument:** Print a usage message and exit non-zero. No API call.
- **Missing environment variable:** Print a message naming the variable (e.g. `Error: OPENROUTER_API_KEY not set`) and exit non-zero. No API call.
- **API error (non-2xx response):** Print the HTTP status code and response body, then exit non-zero.
- **Timeout (no response within 30 seconds) or connection failure:** Print a message describing the failure and exit non-zero.
- **Malformed JSON response:** Print a message saying the response could not be parsed, then exit non-zero.
- **Missing fields** (`choices[0].message.content`, `usage.prompt_tokens`, `usage.completion_tokens`, or `model`): Print a message naming the missing field and exit non-zero.
- **Empty or null answer** (`content` is `null` or empty, e.g. a refusal or filtered response): Print a message saying the model returned no answer, then exit non-zero.

## Cost estimate

- **Pricing:** OpenRouter lists `minimax/minimax-m3` at $0.23/M input tokens and $0.96/M output tokens for the cheapest provider. Routing can use other providers costing up to $0.75/M input and $3.00/M output. (Source: openrouter.ai/minimax/minimax-m3, checked 2026-09-28.)
- **Tokens per call:** One API call per invocation. Measured on 2026-09-28 with a one-sentence question: 186 input and 54 output tokens (output includes any reasoning tokens). Longer questions or answers cost more.
- **Per call:** 186 × $0.23/M + 54 × $0.96/M ≈ $0.00009 (worst-case provider: 186 × $0.75/M + 54 × $3.00/M ≈ $0.00030).
- **Semester:** Assuming ~3 calls per week over a 12-week semester (both are assumptions), 36 calls ≈ $0.003 (worst case ≈ $0.011).

## Out of scope

- Streaming responses
- Conversation history or multi-turn dialogue
- Retries, backoff, or error recovery beyond a single failure message
- Tool/function calling
- Multiple questions per invocation
- Pretty formatting, colors, or interactive prompts
- Request/response logging or debugging output
