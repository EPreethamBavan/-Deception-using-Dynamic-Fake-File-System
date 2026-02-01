"""
UserArtifactGenerator.py - Realistic User Artifact Simulation

Creates comprehensive user artifacts that make the system appear genuinely used.
When an attacker examines the machine, they should find:
- Realistic bash history with timestamps
- SSH known_hosts and config
- Git configuration and repositories
- Browser artifacts (if applicable)
- Recent file access patterns
- Cron jobs and scheduled tasks
- Log files with realistic entries
- Config files with user customizations
"""

import os
import json
import random
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class UserArtifactGenerator:
    """
    Generates comprehensive user artifacts to simulate realistic system usage.
    """

    def __init__(self, personas: Dict, config_dir: str = "."):
        self.personas = personas
        self.config_dir = config_dir
        self.generated_artifacts = []

    def generate_all_artifacts(self, persona_name: str):
        """Generate all artifacts for a specific persona."""
        if persona_name not in self.personas:
            logger.error(f"Unknown persona: {persona_name}")
            return

        persona = self.personas[persona_name]
        home_dir = persona.get('home_dir', f'/home/{persona_name}')

        logger.info(f"Generating artifacts for {persona_name} in {home_dir}")

        # Generate all artifact types
        self._generate_bash_profile(persona_name, persona, home_dir)
        self._generate_ssh_artifacts(persona_name, home_dir)
        self._generate_git_config(persona_name, persona, home_dir)
        self._generate_vim_artifacts(home_dir)
        self._generate_recent_files(persona_name, persona, home_dir)
        self._generate_cron_jobs(persona_name, persona, home_dir)
        self._generate_user_logs(persona_name, home_dir)
        self._generate_shell_aliases(persona_name, persona, home_dir)
        self._generate_project_artifacts(persona_name, persona, home_dir)

    def _ensure_dir(self, path: str):
        """Ensure directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create {path}: {e}")

    def _write_file(self, path: str, content: str, mode: int = 0o644):
        """Write content to file with specified permissions."""
        try:
            self._ensure_dir(os.path.dirname(path))
            with open(path, 'w') as f:
                f.write(content)
            os.chmod(path, mode)
            self.generated_artifacts.append(path)
            logger.debug(f"Created artifact: {path}")
        except Exception as e:
            logger.warning(f"Could not create {path}: {e}")

    def _generate_bash_profile(self, username: str, persona: Dict, home_dir: str):
        """Generate realistic .bashrc and .bash_profile."""

        # Determine user type for appropriate customizations
        is_dev = "dev" in username.lower()
        is_admin = "sys" in username.lower() or "admin" in username.lower()

        # Common aliases based on role
        dev_aliases = """
# Development shortcuts
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -10'
alias gd='git diff'
alias ga='git add'
alias gco='git checkout'

# Docker shortcuts
alias d='docker'
alias dc='docker-compose'
alias dps='docker ps'
alias dimg='docker images'

# Python
alias py='python3'
alias pip='pip3'
alias venv='python3 -m venv'
alias activate='source venv/bin/activate'

# Project shortcuts
alias proj='cd ~/repos/core-services-migration'
alias api='cd ~/repos/backend-api'
"""

        admin_aliases = """
# System administration
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ports='netstat -tulpn'
alias services='systemctl list-units --type=service'
alias logs='journalctl -f'
alias disk='df -h'
alias mem='free -h'

# Safety nets
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Quick edits
alias hosts='sudo vim /etc/hosts'
alias nginx='sudo vim /etc/nginx/nginx.conf'
"""

        common_section = f"""
# History configuration
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTTIMEFORMAT="%F %T "
export HISTCONTROL=ignoreboth:erasedups
shopt -s histappend

# Prompt customization
export PS1='\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '

# Editor
export EDITOR=vim
export VISUAL=vim

# Path additions
export PATH="$HOME/.local/bin:$PATH"

# Load local configurations if they exist
if [ -f ~/.bash_local ]; then
    . ~/.bash_local
fi
"""

        bashrc_content = f"""# ~/.bashrc: executed by bash(1) for non-login shells.
# Last modified: {(datetime.now() - timedelta(days=random.randint(5, 60))).strftime('%Y-%m-%d')}

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

{common_section}

# User-specific aliases
{dev_aliases if is_dev else admin_aliases}

# Custom functions
mkcd() {{
    mkdir -p "$1" && cd "$1"
}}

extract() {{
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"   ;;
            *.tar.gz)    tar xzf "$1"   ;;
            *.bz2)       bunzip2 "$1"   ;;
            *.gz)        gunzip "$1"    ;;
            *.tar)       tar xf "$1"    ;;
            *.zip)       unzip "$1"     ;;
            *)           echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}}

# Welcome message
echo "Welcome back, {username.split('_')[-1].title()}!"
"""

        self._write_file(os.path.join(home_dir, ".bashrc"), bashrc_content)

        # Also create .bash_profile for login shells
        bash_profile = f"""# ~/.bash_profile
# Last login: {(datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%a %b %d %H:%M:%S %Y')}

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
"""
        self._write_file(os.path.join(home_dir, ".bash_profile"), bash_profile)

    def _generate_ssh_artifacts(self, username: str, home_dir: str):
        """Generate SSH configuration files."""
        ssh_dir = os.path.join(home_dir, ".ssh")
        self._ensure_dir(ssh_dir)

        # Generate known_hosts with realistic entries
        known_hosts = []
        servers = [
            ("github.com", "ssh-ed25519", "AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl"),
            ("gitlab.com", "ssh-rsa", "AAAAB3NzaC1yc2EAAAADAQABAAABAQCsj2bN" + "A" * 50),
            ("bitbucket.org", "ssh-rsa", "AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN" + "B" * 50),
            ("192.168.1.10", "ssh-ed25519", "AAAAC3NzaC1lZDI1NTE5AAAA" + "C" * 30),
            ("10.0.0.50", "ssh-rsa", "AAAAB3NzaC1yc2EAAAA" + "D" * 60),
            ("prod-db-01.internal", "ssh-ed25519", "AAAAC3NzaC1lZDI1NTE5AAAA" + "E" * 30),
            ("staging-web.local", "ssh-rsa", "AAAAB3NzaC1yc2EAAAA" + "F" * 60),
        ]

        for host, keytype, key in random.sample(servers, min(5, len(servers))):
            known_hosts.append(f"{host} {keytype} {key}")

        self._write_file(
            os.path.join(ssh_dir, "known_hosts"),
            "\n".join(known_hosts) + "\n",
            mode=0o644
        )

        # Generate SSH config
        ssh_config = f"""# SSH Client Configuration
# Last updated: {(datetime.now() - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d')}

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
    IdentitiesOnly yes

Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

Host gitlab.com
    HostName gitlab.com
    User git
    IdentityFile ~/.ssh/id_ed25519

Host prod-*
    User {username}
    IdentityFile ~/.ssh/id_rsa_prod
    StrictHostKeyChecking yes

Host staging-*
    User {username}
    IdentityFile ~/.ssh/id_rsa_staging
    StrictHostKeyChecking no

Host dev-*
    User {username}
    IdentityFile ~/.ssh/id_rsa_dev
    ForwardAgent yes
"""
        self._write_file(os.path.join(ssh_dir, "config"), ssh_config, mode=0o600)

    def _generate_git_config(self, username: str, persona: Dict, home_dir: str):
        """Generate Git configuration."""
        role = persona.get('role', 'Developer')
        name_part = username.replace('_', ' ').title()

        # Make the name more realistic
        if "alice" in username.lower():
            full_name = "Alice Chen"
        elif "bob" in username.lower():
            full_name = "Robert Martinez"
        else:
            full_name = name_part

        gitconfig = f"""[user]
\tname = {full_name}
\temail = {username}@company.com

[core]
\teditor = vim
\tautocrlf = input
\twhitespace = fix

[init]
\tdefaultBranch = main

[pull]
\trebase = true

[push]
\tdefault = current
\tautoSetupRemote = true

[alias]
\tst = status
\tco = checkout
\tbr = branch
\tci = commit
\tlg = log --oneline --graph --decorate -10
\tdf = diff
\tlast = log -1 HEAD
\tunstage = reset HEAD --
\tundo = checkout --
\tamend = commit --amend --no-edit

[color]
\tui = auto

[diff]
\ttool = vimdiff

[merge]
\ttool = vimdiff
\tconflictstyle = diff3

[credential]
\thelper = cache --timeout=3600

# Work-specific settings
[includeIf "gitdir:~/repos/"]
\tpath = ~/.gitconfig-work
"""
        self._write_file(os.path.join(home_dir, ".gitconfig"), gitconfig)

    def _generate_vim_artifacts(self, home_dir: str):
        """Generate Vim configuration and history."""
        vimrc = """\" Vim configuration
" Last updated dynamically

set nocompatible
filetype plugin indent on
syntax on

" Basic settings
set number
set relativenumber
set cursorline
set showmatch
set incsearch
set hlsearch
set ignorecase
set smartcase

" Indentation
set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent

" UI
set wildmenu
set wildmode=list:longest
set scrolloff=5
set laststatus=2

" File handling
set encoding=utf-8
set fileencoding=utf-8
set backup
set backupdir=~/.vim/backup//
set directory=~/.vim/swap//
set undofile
set undodir=~/.vim/undo//

" Key mappings
let mapleader = " "
nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
nnoremap <leader>e :e<Space>

" Plugin-like behavior (without plugins for simplicity)
" Quick file navigation
nnoremap <leader>f :find<Space>
nnoremap <leader>b :ls<CR>:b<Space>

" Status line
set statusline=%f\ %h%m%r%=%-14.(%l,%c%V%)\ %P
"""
        self._write_file(os.path.join(home_dir, ".vimrc"), vimrc)

        # Create vim directories
        for subdir in ["backup", "swap", "undo"]:
            self._ensure_dir(os.path.join(home_dir, ".vim", subdir))

        # Generate .viminfo with recent files
        recent_files = [
            "~/repos/core-services-migration/src/main.py",
            "~/repos/backend-api/config/settings.yaml",
            "/etc/nginx/nginx.conf",
            "~/repos/core-services-migration/README.md",
            "~/notes/todo.txt",
        ]

        viminfo_marks = "\n".join([
            f"'0  {random.randint(1, 100)}  0  {f}"
            for f in random.sample(recent_files, min(3, len(recent_files)))
        ])

        viminfo = f"""# This viminfo file was generated by Vim
# You may edit it if you're careful!

# Value of 'encoding' when this file was written
*encoding=utf-8

# File marks:
{viminfo_marks}

# Jumplist (newest first):
-'  1  0  ~/repos/core-services-migration/src/main.py

# History of marks within files (newest to oldest):
"""
        self._write_file(os.path.join(home_dir, ".viminfo"), viminfo)

    def _generate_recent_files(self, username: str, persona: Dict, home_dir: str):
        """Generate recently accessed files tracker."""
        # Create .local/share/recently-used.xbel (freedesktop standard)
        local_share = os.path.join(home_dir, ".local", "share")
        self._ensure_dir(local_share)

        recent_files = [
            ("file:///home/{}/repos/core-services-migration/src/main.py".format(username), "text/x-python"),
            ("file:///home/{}/repos/backend-api/config.yaml".format(username), "application/x-yaml"),
            ("file:///home/{}/Documents/notes.txt".format(username), "text/plain"),
            ("file:///var/log/nginx/error.log".format(username), "text/plain"),
        ]

        xbel_entries = []
        for uri, mime in recent_files:
            timestamp = int((datetime.now() - timedelta(hours=random.randint(1, 72))).timestamp())
            xbel_entries.append(f"""  <bookmark href="{uri}" added="{datetime.fromtimestamp(timestamp).isoformat()}" modified="{datetime.fromtimestamp(timestamp).isoformat()}" visited="{datetime.fromtimestamp(timestamp).isoformat()}">
    <info>
      <metadata owner="http://freedesktop.org">
        <mime:mime-type type="{mime}"/>
      </metadata>
    </info>
  </bookmark>""")

        xbel_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info">
{chr(10).join(xbel_entries)}
</xbel>
"""
        self._write_file(os.path.join(local_share, "recently-used.xbel"), xbel_content)

    def _generate_cron_jobs(self, username: str, persona: Dict, home_dir: str):
        """Generate user-specific cron jobs."""
        is_admin = "sys" in username.lower() or "admin" in username.lower()

        if is_admin:
            crontab = f"""# Crontab for {username}
# Last edited: {(datetime.now() - timedelta(days=random.randint(5, 30))).strftime('%Y-%m-%d')}

# Environment
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO={username}@company.com

# Backup home directories - every night at 2 AM
0 2 * * * /usr/local/bin/backup-homes.sh >> /var/log/backup.log 2>&1

# Check disk space - every 4 hours
0 */4 * * * df -h | mail -s "Disk Report" admin@company.com

# Clear temp files older than 7 days - weekly
0 3 * * 0 find /tmp -type f -mtime +7 -delete

# Rotate application logs - daily at midnight
0 0 * * * /usr/sbin/logrotate /etc/logrotate.conf
"""
        else:
            crontab = f"""# Crontab for {username}
# Development tasks

# Sync git repos - every morning at 8 AM
0 8 * * 1-5 cd ~/repos && for d in */; do (cd "$d" && git fetch --all); done

# Run tests - every commit triggers this via CI, but also nightly
0 1 * * * cd ~/repos/core-services-migration && make test > /dev/null 2>&1
"""

        # Write to user's crontab location (simulated)
        cron_dir = os.path.join(home_dir, ".local", "cron")
        self._ensure_dir(cron_dir)
        self._write_file(os.path.join(cron_dir, "crontab"), crontab)

    def _generate_user_logs(self, username: str, home_dir: str):
        """Generate user-specific log files."""
        log_dir = os.path.join(home_dir, ".local", "log")
        self._ensure_dir(log_dir)

        # Generate some realistic log entries
        log_entries = []
        base_time = datetime.now() - timedelta(days=7)

        activities = [
            "Started work session",
            "Pulled latest changes from origin/main",
            "Running test suite",
            "Tests passed: 47/47",
            "Committed changes: Fix authentication bug",
            "Pushed to origin/feature-branch",
            "Code review requested",
            "Merged PR #142",
            "Deployed to staging",
            "Running integration tests",
            "Build successful",
            "Created backup",
            "Updated dependencies",
            "Fixed lint errors",
            "Refactored database module",
        ]

        for i in range(50):
            timestamp = base_time + timedelta(
                days=random.randint(0, 7),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59)
            )
            activity = random.choice(activities)
            log_entries.append(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {activity}")

        log_entries.sort()
        self._write_file(
            os.path.join(log_dir, "activity.log"),
            "\n".join(log_entries) + "\n"
        )

    def _generate_shell_aliases(self, username: str, persona: Dict, home_dir: str):
        """Generate shell alias file."""
        # This is already covered in .bashrc, but add a separate aliases file
        # that some users maintain
        pass

    def _generate_project_artifacts(self, username: str, persona: Dict, home_dir: str):
        """Generate project-related artifacts like TODO files, notes."""
        notes_dir = os.path.join(home_dir, "notes")
        self._ensure_dir(notes_dir)

        # TODO file
        todo_content = f"""# TODO List - {username}
# Last updated: {datetime.now().strftime('%Y-%m-%d')}

## High Priority
- [ ] Fix authentication token refresh issue
- [ ] Review PR #156 - Database migration
- [ ] Update API documentation

## In Progress
- [x] Implement rate limiting middleware
- [ ] Add unit tests for payment module

## Backlog
- [ ] Refactor legacy authentication code
- [ ] Set up monitoring dashboards
- [ ] Document deployment process
- [ ] Investigate memory leak in worker process

## Done (this week)
- [x] Fixed CORS configuration
- [x] Deployed hotfix to production
- [x] Updated dependencies to fix CVE-2024-1234
"""
        self._write_file(os.path.join(notes_dir, "TODO.md"), todo_content)

        # Meeting notes
        meeting_notes = f"""# Meeting Notes

## {(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')} - Sprint Planning

Attendees: Alice, Bob, Sarah, Mike

### Discussion
- Payment gateway integration timeline
- Need to finish by end of month
- Bob will handle infrastructure setup
- Alice on API development

### Action Items
- Alice: Create API endpoints for payment processing
- Bob: Set up staging environment with Stripe test keys
- Sarah: Update user stories in Jira

---

## {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} - Architecture Review

### Decisions
- Moving to microservices for payment module
- Keep monolith for user management (for now)
- Redis for session caching

### Concerns
- Database migration strategy needs more thought
- Need load testing before go-live
"""
        self._write_file(os.path.join(notes_dir, "meetings.md"), meeting_notes)

        # Create a simple scratch pad
        scratch = f"""# Scratch Pad

Quick notes and snippets

## Useful commands
```bash
# Check which process is using a port
lsof -i :8080

# Find large files
find / -type f -size +100M 2>/dev/null

# Watch logs
tail -f /var/log/nginx/error.log | grep -i error
```

## Environment variables to remember
- STRIPE_API_KEY (in .env)
- DATABASE_URL
- REDIS_URL

## Links
- Staging: https://staging.internal.company.com
- Prod: https://api.company.com
- Grafana: http://monitoring.internal:3000

## Random notes
- Jenkins password reset: ask Bob
- VPN config in ~/vpn/company.ovpn
- Slack bot token in password manager
"""
        self._write_file(os.path.join(notes_dir, "scratch.md"), scratch)


class SessionPersistenceManager:
    """
    Manages session persistence for tracking user activity across time.

    Based on shelLM research: "The complete content of each session is saved
    to an external file and used as part of the initial prompt for the next
    session from the same attacker."
    """

    def __init__(self, storage_dir: str = ".sessions"):
        self.storage_dir = storage_dir
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_session_file(self, user_id: str) -> str:
        """Get session file path for a user."""
        safe_id = hashlib.md5(user_id.encode()).hexdigest()[:16]
        return os.path.join(self.storage_dir, f"session_{safe_id}.json")

    def save_session(self, user_id: str, session_data: Dict):
        """Save session data for a user."""
        filepath = self._get_session_file(user_id)
        session_data['last_updated'] = datetime.now().isoformat()

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self, user_id: str) -> Optional[Dict]:
        """Load session data for a user."""
        filepath = self._get_session_file(user_id)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

    def get_command_history(self, user_id: str, limit: int = 50) -> List[str]:
        """Get command history for a user."""
        session = self.load_session(user_id)
        if session and 'command_history' in session:
            return session['command_history'][-limit:]
        return []

    def append_command(self, user_id: str, command: str, output: str = ""):
        """Append a command to user's session history."""
        session = self.load_session(user_id) or {
            'user_id': user_id,
            'created': datetime.now().isoformat(),
            'command_history': [],
            'files_created': [],
            'directories_visited': []
        }

        session['command_history'].append({
            'command': command,
            'output': output[:1000],  # Truncate large outputs
            'timestamp': datetime.now().isoformat()
        })

        self.save_session(user_id, session)


class MetricsCollector:
    """
    Collects metrics for evaluating deception effectiveness.

    Based on research metrics:
    - Attacker dwell time
    - Detection rate
    - Realism score
    - Engagement depth
    """

    def __init__(self, metrics_file: str = "deception_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load existing metrics."""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            'sessions': [],
            'total_commands_executed': 0,
            'fingerprint_attempts': 0,
            'successful_deceptions': 0,
            'detection_events': [],
            'start_time': datetime.now().isoformat()
        }

    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def record_session_start(self, session_id: str, source_ip: str = ""):
        """Record the start of a session."""
        self.metrics['sessions'].append({
            'session_id': session_id,
            'source_ip': source_ip,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'commands': 0,
            'fingerprint_attempts': 0
        })
        self._save_metrics()

    def record_command(self, session_id: str, is_fingerprint: bool = False):
        """Record a command execution."""
        self.metrics['total_commands_executed'] += 1
        if is_fingerprint:
            self.metrics['fingerprint_attempts'] += 1

        # Update session
        for session in self.metrics['sessions']:
            if session['session_id'] == session_id:
                session['commands'] += 1
                if is_fingerprint:
                    session['fingerprint_attempts'] += 1
                break

        self._save_metrics()

    def record_detection(self, detection_type: str, details: str):
        """Record a detection event (attacker detected honeypot)."""
        self.metrics['detection_events'].append({
            'type': detection_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self._save_metrics()

    def record_successful_deception(self):
        """Record a successful deception (attacker fooled)."""
        self.metrics['successful_deceptions'] += 1
        self._save_metrics()

    def get_summary(self) -> Dict:
        """Get metrics summary."""
        total_sessions = len(self.metrics['sessions'])
        detection_count = len(self.metrics['detection_events'])

        return {
            'total_sessions': total_sessions,
            'total_commands': self.metrics['total_commands_executed'],
            'fingerprint_attempts': self.metrics['fingerprint_attempts'],
            'successful_deceptions': self.metrics['successful_deceptions'],
            'detection_events': detection_count,
            'deception_success_rate': (
                self.metrics['successful_deceptions'] / max(total_sessions, 1) * 100
            ),
            'fingerprint_rate': (
                self.metrics['fingerprint_attempts'] / max(self.metrics['total_commands_executed'], 1) * 100
            )
        }
