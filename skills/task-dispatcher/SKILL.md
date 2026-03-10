# Limiter Agent (Task Dispatcher)

This skill provides a **rate-limited task dispatcher** to prevent API quota exhaustion (e.g. Gemini 429 errors).

When you have a large number of tasks or a complex workflow that could trigger rate limits if executed in parallel, use this tool instead of spawning multiple sub-agents directly.

## Usage

The `dispatch_task` tool accepts a JSON array of tasks or a single complex task description. It will:
1.  Spawn a sub-agent for each task.
2.  **Wait 15 seconds** between spawns to respect the global rate limit (approx. 4 requests/minute).

## Tools

### dispatch_task

**Description:** Dispatch a list of tasks with enforced rate limiting (15s delay). Use this for batch processing.

**Parameters:**
- `tasks` (array of strings, required): A list of task descriptions to execute.
- `description` (string, optional): A description of the overall batch job for logging.

**Example:**
```json
{
  "tasks": [
    "Analyze tweet 1 for sentiment",
    "Extract entities from tweet 2",
    "Summarize thread 3"
  ],
  "description": "Batch process 3 tweets"
}
```

## Implementation

The underlying script is `dispatch.js` which uses `openclaw sessions spawn` internally.
