#!/usr/bin/env python3
"""
Setup Dolt SQL Server with Branch ACL for Panini-FS.

This script:
1. Starts dolt sql-server on 127.0.0.1:3306
2. Creates 3 users: public_user, analyst, owner
3. Configures dolt_branch_control for per-branch write isolation
4. Configures dolt_branch_namespace_control to restrict branch creation
5. Verifies the setup

Usage:
    python3 setup_dolt_acl.py [--port PORT] [--db-dir DIR] [--no-server]

The --no-server flag skips starting the server (assumes it's already running).
"""

import argparse
import os
import signal
import subprocess
import sys
import time

# ============================================================
# Configuration
# ============================================================
DEFAULT_PORT = 3306
DEFAULT_DB_DIR = os.path.join(os.path.dirname(__file__), "panini-unified-db")

USERS = {
    "public_user": {
        "password": "pub_panini_2026",
        "grants": "SELECT, INSERT, UPDATE, DELETE, EXECUTE",
        "branches": [("main", "write")],
        "description": "Public tier — write to main only",
    },
    "analyst": {
        "password": "conf_panini_2026",
        "grants": "SELECT, INSERT, UPDATE, DELETE, EXECUTE",
        "branches": [("main", "write"), ("confidential", "write")],
        "description": "Confidential tier — write to main + confidential",
    },
    "owner": {
        "password": "priv_panini_2026",
        "grants": "ALL PRIVILEGES",
        "branches": [("%", "admin")],
        "description": "Private tier — admin on all branches",
    },
}

NAMESPACE_RULES = [
    # Only owner can create private/* branches
    ("private/%", "owner"),
]


def mysql_exec(port, user, password, sql, silent=False):
    """Execute SQL via mysql client. Returns (success, stdout, stderr)."""
    cmd = ["mysql", "-h", "127.0.0.1", "-P", str(port), "-u", user, "--batch", "--skip-ssl-verify-server-cert"]
    if password:
        cmd.append(f"-p{password}")
    cmd.extend(["-e", sql])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if not silent and result.returncode != 0:
        # Filter out the deprecation warning
        stderr = "\n".join(
            l for l in result.stderr.split("\n")
            if "Deprecated program name" not in l
            and "ssl-verify-server-cert" not in l
            and l.strip()
        )
        if stderr:
            print(f"  ⚠️  {stderr[:200]}")
    return result.returncode == 0, result.stdout, result.stderr


def wait_for_server(port, timeout=10):
    """Wait for dolt sql-server to be ready."""
    for i in range(timeout * 2):
        ok, _, _ = mysql_exec(port, "root", "", "SELECT 1;", silent=True)
        if ok:
            return True
        time.sleep(0.5)
    return False


def start_server(db_dir, port):
    """Start dolt sql-server in the background."""
    print(f"\n🚀 Starting dolt sql-server on 127.0.0.1:{port}...")
    print(f"   Database: {db_dir}")

    # Check if already running
    ok, _, _ = mysql_exec(port, "root", "", "SELECT 1;", silent=True)
    if ok:
        print("   ✅ Server already running")
        return None

    # start_new_session=True detaches the server so it survives after this script exits
    log_file = os.path.join(db_dir, "dolt-server.log")
    log_fd = open(log_file, "w")
    proc = subprocess.Popen(
        ["dolt", "sql-server", "--host", "127.0.0.1", "--port", str(port)],
        cwd=db_dir,
        stdout=log_fd,
        stderr=log_fd,
        start_new_session=True,
    )

    if wait_for_server(port):
        print(f"   ✅ Server started (PID {proc.pid})")
        print(f"   📝 Log: {log_file}")
        # Write PID file for easy shutdown
        pid_file = os.path.join(db_dir, "dolt-server.pid")
        with open(pid_file, "w") as f:
            f.write(str(proc.pid))
        return proc
    else:
        proc.kill()
        log_fd.close()
        print("   ❌ Server failed to start")
        print(f"   📝 Check log: {log_file}")
        sys.exit(1)


def setup_users(port, db_name):
    """Create users and configure permissions."""
    print("\n👥 Creating users...")

    for username, config in USERS.items():
        # Create user
        sql = f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{config['password']}';"
        ok, _, _ = mysql_exec(port, "root", "", sql)
        status = "✅" if ok else "❌"
        print(f"   {status} {username}: {config['description']}")

        # Grant SQL privileges
        sql = f"GRANT {config['grants']} ON `{db_name}`.* TO '{username}'@'%';"
        mysql_exec(port, "root", "", sql)

    print("   ✅ All users created and granted")


def setup_branch_control(port, db_name):
    """Configure dolt_branch_control for per-branch write isolation."""
    print("\n🔒 Configuring branch permissions...")

    # Clear existing rules
    sql = f"USE `{db_name}`; DELETE FROM dolt_branch_control; DELETE FROM dolt_branch_namespace_control;"
    mysql_exec(port, "root", "", sql)

    # Add root as admin (so root can manage all branches)
    sql = f"USE `{db_name}`; INSERT INTO dolt_branch_control VALUES ('{db_name}', '%', 'root', 'localhost', 'admin');"
    mysql_exec(port, "root", "", sql)

    # Add per-user branch rules
    for username, config in USERS.items():
        for branch_pattern, perm_level in config["branches"]:
            sql = f"USE `{db_name}`; INSERT INTO dolt_branch_control VALUES ('{db_name}', '{branch_pattern}', '{username}', '%', '{perm_level}');"
            ok, _, _ = mysql_exec(port, "root", "", sql)
            status = "✅" if ok else "❌"
            print(f"   {status} {username} → {branch_pattern} ({perm_level})")

    # Namespace control
    for branch_pattern, username in NAMESPACE_RULES:
        sql = f"USE `{db_name}`; INSERT INTO dolt_branch_namespace_control VALUES ('{db_name}', '{branch_pattern}', '{username}', '%');"
        ok, _, _ = mysql_exec(port, "root", "", sql)
        print(f"   🏷️  Namespace: {branch_pattern} → only {username}")


def verify_setup(port, db_name):
    """Show the final configuration."""
    print("\n📋 Final configuration:")

    print("\n   Branch Control:")
    ok, stdout, _ = mysql_exec(port, "root", "", f"USE `{db_name}`; SELECT * FROM dolt_branch_control;")
    if ok:
        for line in stdout.strip().split("\n")[1:]:  # Skip header
            parts = line.split("\t")
            if len(parts) >= 5:
                print(f"     {parts[2]}@{parts[3]} → branch '{parts[1]}' ({parts[4]})")

    print("\n   Namespace Control:")
    ok, stdout, _ = mysql_exec(port, "root", "", f"USE `{db_name}`; SELECT * FROM dolt_branch_namespace_control;")
    if ok:
        for line in stdout.strip().split("\n")[1:]:
            parts = line.split("\t")
            if len(parts) >= 4:
                print(f"     {parts[2]}@{parts[3]} → can create '{parts[1]}' branches")

    print("\n   MySQL Grants:")
    for username in USERS:
        ok, stdout, _ = mysql_exec(port, "root", "", f"SHOW GRANTS FOR '{username}'@'%';")
        if ok:
            grants = [l for l in stdout.strip().split("\n") if "GRANT" in l and "USAGE" not in l]
            for g in grants:
                print(f"     {username}: {g.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Setup Dolt SQL Server with Branch ACL")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--db-dir", default=DEFAULT_DB_DIR, help="Path to Dolt database directory")
    parser.add_argument("--no-server", action="store_true", help="Skip starting the server")
    parser.add_argument("--db-name", default="panini-unified-db", help="Database name")
    args = parser.parse_args()

    print("=" * 60)
    print("Panini-FS — Dolt SQL Server ACL Setup")
    print("=" * 60)

    server_proc = None
    if not args.no_server:
        server_proc = start_server(args.db_dir, args.port)

    setup_users(args.port, args.db_name)
    setup_branch_control(args.port, args.db_name)
    verify_setup(args.port, args.db_name)

    print("\n" + "=" * 60)
    print("✅ ACL setup complete!")
    print(f"   Server: 127.0.0.1:{args.port}")
    print(f"   Database: {args.db_name}")
    print(f"   Users: {', '.join(USERS.keys())}")
    print("\n   Connection examples:")
    for username, config in USERS.items():
        print(f"     mysql -h 127.0.0.1 -P {args.port} -u {username} -p'{config['password']}'")
    print("=" * 60)

    if server_proc:
        print(f"\n   Server PID: {server_proc.pid} (detached — survives script exit)")
        print(f"   Stop: kill $(cat {os.path.join(args.db_dir, 'dolt-server.pid')})")


if __name__ == "__main__":
    main()
