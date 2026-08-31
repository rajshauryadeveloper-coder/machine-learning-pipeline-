# Welcome to AgentFlow

**If you are a human developer, start here!**

This `.agentflow/` directory contains the workflow rules and context for your AI coding agent. 

## Where to start

1. **Configure your project context:** 
   Open `AGENT_CONTEXT.md` and fill in the placeholders. Tell the agent what framework you use, how to run your tests, and any architectural rules it must follow.
   
2. **Write a task:**
   Go to the `prompts/` folder and create a new markdown file (e.g., `my-feature.md`). Describe exactly what you want the agent to build.

3. **Deploy the agent:**
   Open your AI agent (like Antigravity, Cline, OpenHands, or Aider) and give it this initial prompt:
   > "Please read `.agentflow/AGENTFLOW.md` to understand your workflow, and then execute the task described in `.agentflow/prompts/my-feature.md`."

## How it works

The agent will read `AGENTFLOW.md` which acts as its instruction manual. It will then automatically route itself through the `skills/` (planning, implementing, testing) and document its progress inside the `worklogs/` folder.

If the agent gets stuck or fails a test, it will use the rules defined in `WORKFLOW.md` to retry or escalate the issue back to you.
