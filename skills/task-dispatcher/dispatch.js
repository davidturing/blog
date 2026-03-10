#!/usr/bin/env node
const { execSync } = require('child_process');

// Configuration
// 15 seconds delay between tasks (~4 RPM)
// This is Plan C: "Limiter-Agent" implementation.
const RATE_LIMIT_DELAY_MS = 15000; 
const MAX_RETRIES = 3;

/**
 * Execute a shell command with retries
 */
function runCommand(command) {
  try {
    // Pipe output to stdout so we can see progress in the main session
    return execSync(command, { encoding: 'utf-8', stdio: 'pipe' });
  } catch (error) {
    // If command fails, log but don't crash the dispatcher
    console.error(`Command failed: ${error.message}\nStderr: ${error.stderr}`);
    return JSON.stringify({ error: error.message });
  }
}

/**
 * Sleep helper
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error("Usage: node dispatch.js <json_task_list_or_description>");
    process.exit(1);
  }

  // Combine arguments in case they were split by shell
  let tasksInput = args.join(' ');
  let tasks = [];

  // Try to parse input as JSON array of tasks
  try {
    // Handle potential surrounding quotes from command line passing
    if (tasksInput.startsWith("'") && tasksInput.endsWith("'")) {
        tasksInput = tasksInput.slice(1, -1);
    }
    tasks = JSON.parse(tasksInput);
    
    // If it's an object with a "tasks" key (from tool call structure), extract it
    if (!Array.isArray(tasks) && tasks.tasks && Array.isArray(tasks.tasks)) {
        tasks = tasks.tasks;
    } else if (!Array.isArray(tasks)) {
        // If valid JSON but not array, treat as single task object or description
        tasks = [tasksInput];
    }
  } catch (e) {
    // If not JSON, treat as a raw string description requiring breakdown
    console.log("[Limiter] Input is a raw description. Treating as a single complex task.");
    tasks = [tasksInput];
  }

  console.log(`[Limiter] Received ${tasks.length} tasks. Starting dispatch with ${RATE_LIMIT_DELAY_MS}ms interval...`);

  for (let i = 0; i < tasks.length; i++) {
    const task = tasks[i];
    const taskContent = typeof task === 'string' ? task : JSON.stringify(task);
    
    console.log(`\n[Limiter] Processing task ${i + 1}/${tasks.length}...`);
    
    // Use 'openclaw sessions spawn' to run it in isolation
    // Escape single quotes for shell safety (basic)
    const safeTask = taskContent.replace(/'/g, "'\\''");
    
    // Using openclaw command to spawn a sub-agent
    // We add --json to get structured output if possible, though spawn output varies
    const cmd = `openclaw sessions spawn --task '${safeTask}'`;
    
    console.log(`[Limiter] Spawning agent for: "${taskContent.substring(0, 50)}..."`);
    const output = runCommand(cmd);
    
    console.log(`[Limiter] Task ${i + 1} dispatched.`);

    if (i < tasks.length - 1) {
      console.log(`[Limiter] Sleeping ${RATE_LIMIT_DELAY_MS / 1000}s to respect rate limits...`);
      await new Promise(resolve => setTimeout(resolve, RATE_LIMIT_DELAY_MS));
    }
  }

  console.log("\n[Limiter] All tasks dispatched.");
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
