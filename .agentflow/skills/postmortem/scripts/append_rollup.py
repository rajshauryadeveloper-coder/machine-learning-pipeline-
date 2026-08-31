# Note: The language for this script is swappable (can be .sh or .py).
import argparse
import datetime
import os

def main() -> None:
    parser = argparse.ArgumentParser(description="Append entry to postmortems rollup.")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--outcome", required=True, choices=["merged", "abandoned", "escalated"], help="Outcome of the workflow")
    parser.add_argument("--attempts", type=int, required=True, help="Number of attempts")
    parser.add_argument("--lesson", required=True, help="Key lesson learned")
    parser.add_argument("--details", required=True, help="Details of the lesson")
    
    args = parser.parse_args()
    
    rollup_path = os.path.join(
        os.environ.get("AGENTFLOW_ROOT", ".agentflow"), "postmortems", "ROLLUP.md"
    )
    
    if not os.path.exists(rollup_path):
        # Create it if it doesn't exist
        os.makedirs(os.path.dirname(rollup_path), exist_ok=True)
        with open(rollup_path, 'w') as f:
            f.write("# Postmortems Rollup\n\n<!--\nAgents: Append new entries ABOVE this comment block, keeping the most recent entries at the top.\n-->\n")
            
    with open(rollup_path, 'r') as f:
        content = f.read()
        
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    new_entry = (
        f"### [{date_str}] {args.branch}\n"
        f"- **Branch/Worklog:** `{args.branch}`\n"
        f"- **Outcome:** {args.outcome.capitalize()}\n"
        f"- **Attempts:** {args.attempts}\n"
        f"- **Key Lesson:** {args.lesson} {args.details}\n"
    )

    comment_start = content.find("<!--")
    if comment_start != -1:
        updated_content = (
            content[:comment_start].rstrip() + "\n\n" + new_entry + "\n" + content[comment_start:]
        )
    else:
        updated_content = content.rstrip() + "\n\n" + new_entry + "\n"
        
    with open(rollup_path, 'w') as f:
        f.write(updated_content)
        
    print(f"Successfully appended entry for {args.branch} to {rollup_path}")

if __name__ == "__main__":
    main()
