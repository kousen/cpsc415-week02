"""Send one question to an OpenRouter-compatible chat endpoint and print the answer."""

import json
import os
import sys
import urllib.error
import urllib.request

REQUIRED_ENV = ("OPENROUTER_API_KEY", "CHAT_BASE_URL", "CHAT_MODEL")


def describe_http_error(err: urllib.error.HTTPError) -> str:
    """Turn a 4xx/5xx response into the single failure message the user sees."""
    try:
        return f"HTTP {err.code}: {json.loads(err.read())['error']['message']}"
    except (ValueError, KeyError, TypeError):  # body isn't the usual {"error": {"message": ...}}
        return f"HTTP {err.code} {err.reason}"


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: python chat_client.py "<question>"', file=sys.stderr)
        return 2

    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print(f"missing environment variable(s): {', '.join(missing)}", file=sys.stderr)
        return 1
    api_key, base_url, model = (os.environ[name] for name in REQUIRED_ENV)

    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(
            {"model": model, "messages": [{"role": "user", "content": sys.argv[1]}]}
        ).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.load(response)
        answer = body["choices"][0]["message"]["content"]
        usage = body["usage"]
        counts = (usage["prompt_tokens"], usage["completion_tokens"])
    except urllib.error.HTTPError as err:
        print(f"request failed: {describe_http_error(err)}", file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"request failed: {err.reason}", file=sys.stderr)
        return 1
    except (KeyError, IndexError, TypeError, ValueError) as err:
        print(f"unexpected response: {err!r}", file=sys.stderr)
        return 1

    print(answer)
    print(f"model={body.get('model', model)} input_tokens={counts[0]} output_tokens={counts[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
