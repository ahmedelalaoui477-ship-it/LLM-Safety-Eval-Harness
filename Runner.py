import os
import json
import time
import uuid
import random
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import (
    OpenAI,
    RateLimitError,
    APIConnectionError,
    InternalServerError,
    BadRequestError,
)

load_dotenv()

BASE_URL = "https://integrate.api.nvidia.com/v1"
MODELS = {
    "small": "openai/gpt-oss-20b",
    "large": "nvidia/nemotron-3-super-120b-a12b",
}
SCHEDULE = [(0.0, 2), (1.0, 5)]   # (temperature, how many samples)
MAX_TOKENS = 8192
SEED = 42
DELAY_SECONDS = 2
MAX_RETRIES = 5
PROMPT_BANK = "prompts/prompt_bank.jsonl"
LOG_PATH = "logs/raw_calls.jsonl"

def load_prompts(path):
    prompts = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            if p["prompt_id"] in seen:
                raise ValueError(f"Duplicate prompt_id: {p['prompt_id']}")
            seen.add(p["prompt_id"])
            prompts.append(p)
    return prompts

def make_plan(prompts, model_id):
    jobs = []
    for p in prompts:
        for temperature, n_samples in SCHEDULE:
            for sample_index in range(n_samples):
                run_key = f"{model_id}|{p['prompt_id']}|{temperature}|{sample_index}"
                jobs.append({
                    "run_key": run_key,
                    "prompt_id": p["prompt_id"],
                    "prompt_text": p["text"],
                    "temperature": temperature,
                    "sample_index": sample_index,
                })
    return jobs

def load_done_keys(log_path):
    done = set()
    if not os.path.exists(log_path):
        return done
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("error") is None:
                done.add(rec["run_key"])
    return done

def call_model(client, model_id, job):
    kwargs = dict(
        model=model_id,
        messages=[{"role": "user", "content": job["prompt_text"]}],
        temperature=job["temperature"],
        max_tokens=MAX_TOKENS,
    )
    if SEED is not None:
        kwargs["seed"] = SEED

    start = time.time()
    response = client.chat.completions.create(**kwargs)
    latency = time.time() - start

    choice = response.choices[0]
    message = choice.message
    usage = response.usage

    reasoning_text = (
        getattr(message, "reasoning_content", None)
        or getattr(message, "reasoning", None)
    )
    details = getattr(usage, "completion_tokens_details", None)
    reasoning_tokens = getattr(details, "reasoning_tokens", None) if details else None

    return {
        "batch_id": job["batch_id"],
        "run_key": job["run_key"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_requested": model_id,
        "model_returned": response.model,
        "response_id": response.id,
        "prompt_id": job["prompt_id"],
        "prompt_text": job["prompt_text"],
        "temperature": job["temperature"],
        "sample_index": job["sample_index"],
        "max_tokens": MAX_TOKENS,
        "seed_sent": SEED,
        "content": message.content,
        "reasoning_text": reasoning_text,
        "finish_reason": choice.finish_reason,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": usage.total_tokens,
        "latency_s": round(latency, 2),
        "error": None,
        "raw_response": response.model_dump(),
    }

def error_record(job, model_id, message):
    return {
        "batch_id": job["batch_id"],
        "run_key": job["run_key"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_requested": model_id,
        "prompt_id": job["prompt_id"],
        "temperature": job["temperature"],
        "sample_index": job["sample_index"],
        "content": None,
        "finish_reason": None,
        "error": message,
    }


def call_with_retry(client, model_id, job):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return call_model(client, model_id, job)
        except (RateLimitError, APIConnectionError, InternalServerError) as e:
            last_error = f"{type(e).__name__}: {e}"
            wait = (2 ** attempt) + random.random()
            print(f"  attempt {attempt} failed ({type(e).__name__}), waiting {wait:.1f}s")
            time.sleep(wait)
        except BadRequestError as e:
            return error_record(job, model_id, f"BadRequestError: {e}")
    return error_record(job, model_id, f"Gave up after {MAX_RETRIES} tries: {last_error}")
    
def append_record(log_path, record):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS.keys(), required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    model_id = MODELS[args.model]
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["NVIDIA_API_KEY"])
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    prompts = load_prompts(PROMPT_BANK)
    jobs = make_plan(prompts, model_id)
    done = load_done_keys(LOG_PATH)
    todo = [j for j in jobs if j["run_key"] not in done]
    if args.limit is not None:
        todo = todo[: args.limit]

    batch_id = uuid.uuid4().hex[:8]
    print(f"Model: {model_id} | batch {batch_id}")
    print(f"Planned: {len(jobs)} | already done: {len(done)} | to run now: {len(todo)}")

    errors = 0
    for i, job in enumerate(todo, start=1):
        job["batch_id"] = batch_id
        record = call_with_retry(client, model_id, job)
        append_record(LOG_PATH, record)
        if record["error"] is not None:
            errors += 1
        print(f"[{i}/{len(todo)}] {job['run_key']} "
              f"finish={record.get('finish_reason')} error={record['error']}")
        time.sleep(DELAY_SECONDS)

    print(f"Finished. Errors this batch: {errors}")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()