"""
AntiFingerprint.py - Anti-Detection and Realism Module

Based on research from:
- SANS ISC: "Understanding SSH Honeypot Logs: Attackers Fingerprinting Honeypots"
- shelLM: "LLM in the Shell: Generative Honeypots" (arXiv 2309.00155)
- "Gotta catch 'em all: A Multistage Framework for honeypot fingerprinting"

This module implements countermeasures against common honeypot fingerprinting techniques.
"""

import os
import random
import time
import hashlib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AntiFingerprintManager:
    """
    Implements anti-fingerprinting techniques to make the deception more realistic.

    Key techniques countered:
    1. /proc/self/exe inspection (used by attackers to detect Cowrie)
    2. busybox binary checks
    3. /dev/shm ramdisk tests
    4. Timing analysis attacks
    5. File system structure analysis
    """

    def __init__(self, config_dir="."):
        self.config_dir = config_dir
        self.proc_cache = {}
        self._init_proc_filesystem()
        self._init_system_files()

    def _init_proc_filesystem(self):
        """
        Creates realistic /proc entries that attackers commonly check.

        Attackers use commands like:
        - cat /proc/self/exe
        - cat /proc/version
        - cat /proc/cpuinfo
        - cat /proc/meminfo
        """
        # Realistic kernel version
        kernel_versions = [
            "5.15.0-91-generic",
            "5.4.0-170-generic",
            "6.5.0-14-generic",
            "5.10.0-27-amd64"
        ]

        self.proc_cache = {
            "/proc/version": self._generate_proc_version(random.choice(kernel_versions)),
            "/proc/cpuinfo": self._generate_cpuinfo(),
            "/proc/meminfo": self._generate_meminfo(),
            "/proc/uptime": self._generate_uptime(),
            "/proc/loadavg": self._generate_loadavg(),
            "/proc/mounts": self._generate_mounts(),
            "/proc/cmdline": self._generate_cmdline(),
            "/proc/filesystems": self._generate_filesystems(),
        }

    def _generate_proc_version(self, kernel_version):
        """Generate realistic /proc/version content."""
        gcc_versions = ["9.4.0", "10.3.0", "11.4.0", "12.3.0"]
        gcc = random.choice(gcc_versions)

        build_date = datetime.now() - timedelta(days=random.randint(30, 365))
        date_str = build_date.strftime("%a %b %d %H:%M:%S UTC %Y")

        return f"Linux version {kernel_version} (buildd@lcy02-amd64-XXX) (gcc (Ubuntu {gcc}) {gcc}, GNU ld (GNU Binutils for Ubuntu) 2.38) #1 SMP {date_str}\n"

    def _generate_cpuinfo(self):
        """Generate realistic /proc/cpuinfo content."""
        cpu_models = [
            "Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz",
            "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
            "AMD EPYC 7502 32-Core Processor",
            "Intel(R) Xeon(R) Gold 6248 CPU @ 2.50GHz"
        ]

        model = random.choice(cpu_models)
        cores = random.choice([2, 4, 8, 16])

        cpuinfo = ""
        for i in range(cores):
            cpuinfo += f"""processor\t: {i}
vendor_id\t: {'GenuineIntel' if 'Intel' in model else 'AuthenticAMD'}
cpu family\t: 6
model\t\t: 85
model name\t: {model}
stepping\t: 7
microcode\t: 0x{random.randint(0x5000, 0x5fff):x}
cpu MHz\t\t: {random.uniform(2000, 3500):.3f}
cache size\t: {random.choice([25344, 35840, 16384])} KB
physical id\t: 0
siblings\t: {cores}
core id\t\t: {i}
cpu cores\t: {cores}
bogomips\t: {random.uniform(4000, 6000):.2f}
flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl xtopology

"""
        return cpuinfo

    def _generate_meminfo(self):
        """Generate realistic /proc/meminfo content."""
        total_gb = random.choice([4, 8, 16, 32, 64])
        total_kb = total_gb * 1024 * 1024

        # Realistic memory distribution
        free_pct = random.uniform(0.15, 0.45)
        buffers_pct = random.uniform(0.02, 0.08)
        cached_pct = random.uniform(0.20, 0.40)

        free_kb = int(total_kb * free_pct)
        buffers_kb = int(total_kb * buffers_pct)
        cached_kb = int(total_kb * cached_pct)
        available_kb = free_kb + buffers_kb + int(cached_kb * 0.8)

        return f"""MemTotal:       {total_kb} kB
MemFree:        {free_kb} kB
MemAvailable:   {available_kb} kB
Buffers:        {buffers_kb} kB
Cached:         {cached_kb} kB
SwapCached:     {random.randint(0, 50000)} kB
Active:         {int(total_kb * 0.35)} kB
Inactive:       {int(total_kb * 0.25)} kB
SwapTotal:      {total_kb // 2} kB
SwapFree:       {total_kb // 2 - random.randint(0, 100000)} kB
Dirty:          {random.randint(0, 1000)} kB
Writeback:      0 kB
AnonPages:      {int(total_kb * 0.20)} kB
Mapped:         {random.randint(50000, 200000)} kB
Shmem:          {random.randint(10000, 100000)} kB
"""

    def _generate_uptime(self):
        """Generate realistic /proc/uptime content."""
        # System uptime in seconds (1-90 days)
        uptime_secs = random.randint(86400, 86400 * 90)
        idle_secs = uptime_secs * random.uniform(0.85, 0.98)
        return f"{uptime_secs:.2f} {idle_secs:.2f}\n"

    def _generate_loadavg(self):
        """Generate realistic /proc/loadavg content."""
        load1 = random.uniform(0.01, 2.5)
        load5 = load1 * random.uniform(0.8, 1.2)
        load15 = load5 * random.uniform(0.8, 1.1)
        running = random.randint(1, 5)
        total = random.randint(150, 400)
        last_pid = random.randint(10000, 99999)
        return f"{load1:.2f} {load5:.2f} {load15:.2f} {running}/{total} {last_pid}\n"

    def _generate_mounts(self):
        """Generate realistic /proc/mounts content (avoiding UML honeypot signatures)."""
        # NOTE: UML honeypots have distinct /proc/mounts signatures - we avoid those
        return """/dev/sda1 / ext4 rw,relatime,errors=remount-ro 0 0
devtmpfs /dev devtmpfs rw,nosuid,size=4096k,nr_inodes=1048576,mode=755,inode64 0 0
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
tmpfs /run tmpfs rw,nosuid,nodev,size=1630744k,nr_inodes=819200,mode=755,inode64 0 0
tmpfs /dev/shm tmpfs rw,nosuid,nodev,inode64 0 0
tmpfs /run/lock tmpfs rw,nosuid,nodev,noexec,relatime,size=5120k,inode64 0 0
cgroup2 /sys/fs/cgroup cgroup2 rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot 0 0
"""

    def _generate_cmdline(self):
        """Generate realistic /proc/cmdline content (avoiding UML signatures)."""
        # NOTE: UML honeypots have "uml" in cmdline - we avoid that
        root_uuid = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        return f"BOOT_IMAGE=/vmlinuz-5.15.0-91-generic root=UUID={root_uuid}-{root_uuid[:4]}-{root_uuid[4:8]}-{root_uuid[:4]}-{root_uuid}{root_uuid[:4]} ro quiet splash\n"

    def _generate_filesystems(self):
        """Generate realistic /proc/filesystems content."""
        return """nodev\tsysfs
nodev\ttmpfs
nodev\tbdev
nodev\tproc
nodev\tcgroup
nodev\tcgroup2
nodev\tcpuset
nodev\tdevtmpfs
nodev\tdevpts
nodev\tsecurityfs
nodev\tsockfs
nodev\tdebugfs
nodev\ttracefs
nodev\thugetlbfs
nodev\tmqueue
nodev\tpstore
nodev\tautofs
\text3
\text4
\text2
\tvfat
\tfuseblk
nodev\tfuse
nodev\tfusectl
nodev\tefivarfs
"""

    def _init_system_files(self):
        """Initialize other system files that attackers might check."""
        self.system_files = {
            "/etc/os-release": self._generate_os_release(),
            "/etc/passwd": self._generate_passwd(),
            "/etc/hostname": self._generate_hostname(),
            "/etc/hosts": self._generate_hosts(),
        }

    def _generate_os_release(self):
        """Generate realistic /etc/os-release content."""
        distros = [
            ("Ubuntu", "22.04.3 LTS", "Jammy Jellyfish", "ubuntu"),
            ("Ubuntu", "20.04.6 LTS", "Focal Fossa", "ubuntu"),
            ("Debian GNU/Linux", "12", "bookworm", "debian"),
            ("CentOS Stream", "9", "CentOS Stream 9", "centos"),
        ]

        name, version, codename, id_name = random.choice(distros)

        return f"""PRETTY_NAME="{name} {version} ({codename})"
NAME="{name}"
VERSION_ID="{version.split()[0]}"
VERSION="{version} ({codename})"
VERSION_CODENAME={codename.lower().replace(' ', '')}
ID={id_name}
ID_LIKE=debian
HOME_URL="https://www.{id_name}.com/"
SUPPORT_URL="https://help.{id_name}.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/{id_name}/"
PRIVACY_POLICY_URL="https://www.{id_name}.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME={codename.lower().replace(' ', '')}
"""

    def _generate_passwd(self):
        """Generate realistic /etc/passwd with our fake personas."""
        base_passwd = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
dev_alice:x:1000:1000:Alice Developer,,,:/home/dev_alice:/bin/bash
sys_bob:x:1001:1001:Bob SysAdmin,,,:/home/sys_bob:/bin/bash
jenkins:x:1002:1002:Jenkins CI,,,:/var/lib/jenkins:/bin/bash
"""
        return base_passwd

    def _generate_hostname(self):
        """Generate a realistic hostname."""
        prefixes = ["srv", "web", "app", "db", "dev", "prod", "staging"]
        suffixes = ["01", "02", "03", "a", "b", "primary", "secondary"]
        domains = ["internal", "local", "corp"]

        return f"{random.choice(prefixes)}-{random.choice(suffixes)}.{random.choice(domains)}\n"

    def _generate_hosts(self):
        """Generate realistic /etc/hosts content."""
        hostname = self._generate_hostname().strip()
        return f"""127.0.0.1\tlocalhost
127.0.1.1\t{hostname}

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""

    def get_proc_file(self, path):
        """Get content for a /proc file."""
        # Regenerate dynamic files each time
        if path == "/proc/uptime":
            return self._generate_uptime()
        elif path == "/proc/loadavg":
            return self._generate_loadavg()
        elif path == "/proc/meminfo":
            return self._generate_meminfo()

        return self.proc_cache.get(path)

    def get_system_file(self, path):
        """Get content for a system file."""
        return self.system_files.get(path)


class RealisticTimestampManager:
    """
    Manages realistic timestamps for bash history and file modifications.

    Based on research showing that:
    1. Consistent timestamps across sessions reveal simulation
    2. Real users have patterns (work hours, breaks, weekends)
    3. Command timing follows natural rhythms
    """

    def __init__(self, persona_data):
        self.work_hours = persona_data.get('work_hours', [9, 17])
        self.base_time = datetime.now()
        self.last_command_time = None

    def get_next_timestamp(self, command_type="normal"):
        """
        Generate a realistic timestamp for the next command.

        Command types:
        - normal: Regular command (1-30 second gap)
        - thinking: After error or complex task (30-120 seconds)
        - break: Coffee break / distraction (5-30 minutes)
        - new_session: Start of new work session
        """
        if self.last_command_time is None:
            self.last_command_time = self._get_work_time()
            return self.last_command_time

        if command_type == "normal":
            # Most commands are quick succession
            gap = random.uniform(1, 30)
        elif command_type == "thinking":
            # After errors, users pause to think
            gap = random.uniform(30, 120)
        elif command_type == "break":
            # Occasional breaks
            gap = random.uniform(300, 1800)
        elif command_type == "new_session":
            # New session after hours/days
            gap = random.uniform(3600, 86400)
        else:
            gap = random.uniform(1, 30)

        self.last_command_time += timedelta(seconds=gap)

        # Ensure we're in work hours
        while not self._is_work_hours(self.last_command_time):
            # Skip to next work day
            self.last_command_time += timedelta(hours=1)

        return self.last_command_time

    def _get_work_time(self):
        """Get a timestamp within work hours."""
        now = datetime.now()
        start_hour, end_hour = self.work_hours

        if start_hour <= now.hour < end_hour:
            return now

        # Move to next work period
        if now.hour >= end_hour:
            # Next day
            next_day = now + timedelta(days=1)
            return next_day.replace(hour=start_hour, minute=random.randint(0, 30))
        else:
            # Later today
            return now.replace(hour=start_hour, minute=random.randint(0, 30))

    def _is_work_hours(self, dt):
        """Check if datetime is within work hours."""
        start_hour, end_hour = self.work_hours

        # Skip weekends (optional - can be configured)
        # if dt.weekday() >= 5:
        #     return False

        return start_hour <= dt.hour < end_hour

    def format_for_history(self, timestamp):
        """Format timestamp for bash history (HISTTIMEFORMAT style)."""
        return timestamp.strftime("#%s")  # Unix epoch format

    def format_human_readable(self, timestamp):
        """Format timestamp for human-readable display."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")


class BashHistoryManager:
    """
    Manages realistic bash history with timestamps.

    Features:
    - HISTTIMEFORMAT-aware timestamp prefixes
    - Realistic command patterns
    - Typo simulation
    - Command frequency analysis
    """

    COMMON_TYPOS = {
        "git": ["gti", "got", "gir"],
        "docker": ["dockr", "docekr", "dokcer"],
        "kubectl": ["kubetcl", "kubctl", "kuberctl"],
        "python": ["pyhton", "pytohn", "pyton"],
        "systemctl": ["systemclt", "systmctl", "systemctrl"],
        "ls": ["sl", "ks"],
        "cd": ["dc", "cs"],
        "cat": ["cta", "act"],
        "grep": ["gerp", "gre"],
        "vim": ["vom", "vmi", "cim"],
    }

    # Commands that typically follow each other
    COMMAND_SEQUENCES = [
        ["cd {dir}", "ls -la", "pwd"],
        ["git status", "git add .", "git commit -m '{msg}'"],
        ["vim {file}", "cat {file}"],
        ["docker build -t {tag} .", "docker push {tag}"],
        ["python {script}", "echo $?"],
        ["make", "make test", "make install"],
    ]

    def __init__(self, username, home_dir, persona_data):
        self.username = username
        self.home_dir = home_dir
        self.history_file = os.path.join(home_dir, ".bash_history")
        self.timestamp_manager = RealisticTimestampManager(persona_data)
        self.history_buffer = []

    def add_command(self, command, add_typo_chance=0.05):
        """
        Add a command to history with realistic timestamp.

        Args:
            command: The command to add
            add_typo_chance: Probability of inserting a typo before the real command
        """
        # Occasionally add a typo first (then correction)
        if random.random() < add_typo_chance:
            typo_cmd = self._generate_typo(command)
            if typo_cmd != command:
                ts = self.timestamp_manager.get_next_timestamp("normal")
                self.history_buffer.append((ts, typo_cmd))
                # Quick correction
                ts = self.timestamp_manager.get_next_timestamp("normal")
        else:
            ts = self.timestamp_manager.get_next_timestamp("normal")

        self.history_buffer.append((ts, command))

    def _generate_typo(self, command):
        """Generate a typo version of a command."""
        parts = command.split()
        if not parts:
            return command

        base_cmd = parts[0]
        if base_cmd in self.COMMON_TYPOS:
            typo = random.choice(self.COMMON_TYPOS[base_cmd])
            return command.replace(base_cmd, typo, 1)

        return command

    def flush_to_file(self):
        """Write buffered history to file with timestamps."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            with open(self.history_file, "a") as f:
                for timestamp, command in self.history_buffer:
                    # Write timestamp line (HISTTIMEFORMAT format)
                    f.write(f"#{int(timestamp.timestamp())}\n")
                    f.write(f"{command}\n")

            self.history_buffer.clear()
            logger.debug(f"Flushed history to {self.history_file}")

        except Exception as e:
            logger.error(f"Failed to write history: {e}")

    def get_recent_commands(self, count=10):
        """Get recent commands from history."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    lines = f.readlines()

                # Filter out timestamp lines
                commands = [l.strip() for l in lines if not l.startswith("#")]
                return commands[-count:]
        except:
            pass
        return []


class AttackerBehaviorDetector:
    """
    Detects attacker fingerprinting attempts and adapts responses.

    Based on SANS ISC research on common fingerprinting commands.
    """

    FINGERPRINT_PATTERNS = [
        # Cowrie detection
        (r"busybox.*dd.*if=.*\$SHELL", "cowrie_detection", "high"),
        (r"dd.*if=/proc/self/exe", "binary_inspection", "high"),
        (r"cat /proc/self/exe", "binary_inspection", "high"),

        # UML/VM detection
        (r"cat /proc/mounts", "vm_detection", "medium"),
        (r"cat /proc/cmdline", "vm_detection", "medium"),
        (r"dmesg.*uml", "uml_detection", "high"),

        # Honeypot enumeration
        (r"ls /honeypot", "honeypot_search", "critical"),
        (r"find.*cowrie", "cowrie_search", "critical"),
        (r"which cowrie", "cowrie_search", "critical"),

        # Environment probing
        (r"env\s*$", "env_dump", "low"),
        (r"printenv", "env_dump", "low"),
        (r"cat /etc/passwd", "user_enum", "low"),

        # Network/system probing
        (r"netstat.*-tulpn", "network_enum", "medium"),
        (r"ss.*-tulpn", "network_enum", "medium"),
        (r"ps aux", "process_enum", "low"),
    ]

    def __init__(self):
        self.detection_log = []
        self.threat_score = 0
        import re
        self.compiled_patterns = [
            (re.compile(p, re.IGNORECASE), name, severity)
            for p, name, severity in self.FINGERPRINT_PATTERNS
        ]

    def analyze_command(self, command):
        """
        Analyze a command for fingerprinting attempts.

        Returns:
            dict: Detection result with threat info
        """
        for pattern, name, severity in self.compiled_patterns:
            if pattern.search(command):
                detection = {
                    "command": command,
                    "pattern": name,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                }
                self.detection_log.append(detection)
                self._update_threat_score(severity)

                logger.warning(f"[FINGERPRINT DETECTED] {name}: {command}")
                return detection

        return None

    def _update_threat_score(self, severity):
        """Update cumulative threat score."""
        scores = {"low": 1, "medium": 3, "high": 5, "critical": 10}
        self.threat_score += scores.get(severity, 1)

    def get_threat_level(self):
        """Get current threat level based on accumulated score."""
        if self.threat_score >= 20:
            return "critical"
        elif self.threat_score >= 10:
            return "high"
        elif self.threat_score >= 5:
            return "medium"
        elif self.threat_score > 0:
            return "low"
        return "none"

    def should_adapt_behavior(self):
        """Determine if we should change deception strategy."""
        return self.threat_score >= 5

    def get_detection_summary(self):
        """Get summary of all detections."""
        return {
            "total_detections": len(self.detection_log),
            "threat_score": self.threat_score,
            "threat_level": self.get_threat_level(),
            "recent_detections": self.detection_log[-10:]
        }
