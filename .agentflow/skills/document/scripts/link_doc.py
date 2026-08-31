# Note: The language for this script is swappable (can be .sh or .py).
import argparse
import os

def main() -> None:
    parser = argparse.ArgumentParser(description="Link documentation to worklog.")
    parser.add_argument("--worklog", required=True, help="Path to SUMMARY.md")
    parser.add_argument("--doc-path", required=True, help="Path to generated doc")
    args = parser.parse_args()

    worklog_path = args.worklog
    doc_path = args.doc_path

    if not os.path.exists(worklog_path):
        print(f"Error: Worklog {worklog_path} not found.")
        return

    with open(worklog_path, 'r') as f:
        content = f.read()

    artifacts_section = "## Artifacts"
    link_entry = f"- [{os.path.basename(doc_path)}]({doc_path}) — generated documentation"

    if artifacts_section in content:
        # Append to existing Artifacts section
        parts = content.split(artifacts_section)
        # Find next section or end of file
        next_section_idx = parts[1].find("\n## ")
        
        if next_section_idx != -1:
            updated_content = (
                parts[0] + artifacts_section + 
                parts[1][:next_section_idx] + 
                f"\n{link_entry}\n" + 
                parts[1][next_section_idx:]
            )
        else:
            updated_content = content + f"\n{link_entry}\n"
    else:
        # Create Artifacts section at the end
        updated_content = content + f"\n\n{artifacts_section}\n{link_entry}\n"

    with open(worklog_path, 'w') as f:
        f.write(updated_content)

    print(f"Successfully linked {doc_path} in {worklog_path}")

if __name__ == "__main__":
    main()
