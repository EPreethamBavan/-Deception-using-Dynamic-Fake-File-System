
import os
import zipfile
import shutil

def create_deployment_zip():
    OUTPUT_FILENAME = "deception-engine-deploy.zip"
    
    # Valid files/dirs to include (allowlisting approach for safety)
    INCLUDES = [
        "sys_core.py",
        "LLM_Provider.py",
        "ContentManager.py",
        "StrategyManager.py",
        "ActiveDefense.py",
        "AntiFingerprint.py",
        "PromptEngine.py",
        "UserArtifactGenerator.py",
        "setup_linux.sh",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT.md",
        "config",
        "tests",
        "docs",
        "docs",
        "logs",
        "skills"
    ]

    EXCLUDES = [
        "config/.env",       # SECRETS
        "config/project_state.json", # Runtime state
        "config/state.json",         # Runtime state
        "__pycache__",
        ".git",
        ".DS_Store",
        ".venv",
        "venv",
        "legacy_archive",
        "legacy_archive_2"
    ]

    print(f"Creating {OUTPUT_FILENAME}...")

    with zipfile.ZipFile(OUTPUT_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add root files
        for item in INCLUDES:
            if os.path.isfile(item):
                print(f"  Adding file: {item}")
                zipf.write(item)
            elif os.path.isdir(item):
                print(f"  Adding directory: {item}")
                for root, dirs, files in os.walk(item):
                    # Filter excluded directories in-place
                    dirs[:] = [d for d in dirs if d not in EXCLUDES and not d.startswith("__")]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Check exclusions
                        is_excluded = False
                        # Normalize path for check
                        norm_path = file_path.replace("\\", "/")
                        for excl in EXCLUDES:
                            if excl in norm_path:
                                is_excluded = True
                                break
                        
                        if not is_excluded:
                            zipf.write(file_path)
    
    print("Done!")

if __name__ == "__main__":
    create_deployment_zip()
