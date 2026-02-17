#!/usr/bin/env python3
"""
Test Dolt Branch ACL — verify write isolation per user per branch.

This test validates that:
- public_user can ONLY write to 'main'
- analyst can write to 'main' + 'confidential'
- owner can write to ALL branches (admin)
- Only owner can create private/* branches (namespace control)
- ALL users can READ all branches (Dolt design: read is universal)

Prerequisites:
  1. dolt sql-server running on 127.0.0.1:3306
  2. setup_dolt_acl.py has been run to create users and permissions

Usage:
    python3 test_branch_acl.py [--port PORT]
"""

import argparse
import subprocess
import sys

RESULTS = []
DB = "panini-unified-db"


def mysql_cmd(port, user, password, sql):
    """Run SQL as a given user, return (success, output)."""
    cmd = [
        "mysql", "-h", "127.0.0.1", "-P", str(port),
        "-u", user,
        "--skip-ssl-verify-server-cert", "--batch",
    ]
    if password:
        cmd.extend([f"-p{password}"])
    cmd.extend(["-e", sql])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    success = result.returncode == 0
    output = (result.stdout + result.stderr).strip()
    return success, output


def test(port, name, user, password, sql, should_succeed):
    """Run a test and record pass/fail."""
    success, output = mysql_cmd(port, user, password, sql)
    passed = success == should_succeed
    status = "✅ PASS" if passed else "❌ FAIL"
    RESULTS.append((name, status, passed))
    detail = "OK" if passed else (
        f"expected {'success' if should_succeed else 'failure'}, "
        f"got {'success' if success else 'failure'}"
    )
    print(f"  {status} {name}: {detail}")
    if not passed:
        err_lines = [
            l for l in output.split("\n")
            if "ERROR" in l or "denied" in l.lower()
        ]
        for l in err_lines[:3]:
            print(f"       → {l.strip()[:150]}")
    return passed


def run_tests(port):
    """Run the full ACL test suite."""
    db = f"`{DB}`"

    print("=" * 70)
    print("TEST SUITE: Dolt Branch ACL — Write Isolation")
    print("=" * 70)

    # ── GROUP 1: public_user (write: main only) ─────────────
    print("\n👤 public_user (write: main only)")
    print("-" * 50)

    test(port, "Read main (SELECT)", "public_user", "pub_panini_2026",
         f"USE {db}; SELECT COUNT(*) AS cnt FROM dhatu_definitions;", True)

    test(port, "Read confidential (SELECT)", "public_user", "pub_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('confidential'); "
         f"SELECT COUNT(*) AS cnt FROM semantic_mappings;", True)

    test(port, "Write main ✓", "public_user", "pub_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('main'); "
         f"INSERT INTO public_statistics (stat_type, scope, metrics) "
         f"VALUES ('acl_test', 'global', '{{\"v\": 42}}');", True)

    test(port, "Write confidential ✗", "public_user", "pub_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('confidential'); "
         f"INSERT INTO semantic_mappings (content_hash, source_text, language, "
         f"dhatu_signature, semantic_hash) "
         f"VALUES ('aclh1', 'test', 'en', '{{}}', 'sh1');", False)

    test(port, "Write private/stephane ✗", "public_user", "pub_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('private/stephane'); "
         f"INSERT INTO user_files (file_hash, file_path, file_name, file_size, owner) "
         f"VALUES ('aclh2', '/x', 'x.txt', 10, 'hack');", False)

    # ── GROUP 2: analyst (write: main + confidential) ────────
    print("\n👤 analyst (write: main + confidential)")
    print("-" * 50)

    test(port, "Write main ✓", "analyst", "conf_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('main'); "
         f"INSERT INTO public_statistics (stat_type, scope, metrics) "
         f"VALUES ('acl_analyst', 'global', '{{\"v\": 99}}');", True)

    test(port, "Write confidential ✓", "analyst", "conf_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('confidential'); "
         f"INSERT INTO semantic_mappings (content_hash, source_text, language, "
         f"dhatu_signature, semantic_hash) "
         f"VALUES ('aclh3', 'analyst', 'fr', '{{}}', 'sh3');", True)

    test(port, "Write private/stephane ✗", "analyst", "conf_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('private/stephane'); "
         f"INSERT INTO user_files (file_hash, file_path, file_name, file_size, owner) "
         f"VALUES ('aclh4', '/y', 'y.txt', 20, 'hack');", False)

    # ── GROUP 3: owner (admin: all branches) ─────────────────
    print("\n👤 owner (admin: all branches)")
    print("-" * 50)

    test(port, "Write main ✓", "owner", "priv_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('main'); "
         f"INSERT INTO public_statistics (stat_type, scope, metrics) "
         f"VALUES ('acl_owner', 'global', '{{\"v\": 77}}');", True)

    test(port, "Write confidential ✓", "owner", "priv_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('confidential'); "
         f"INSERT INTO semantic_mappings (content_hash, source_text, language, "
         f"dhatu_signature, semantic_hash) "
         f"VALUES ('aclh5', 'owner', 'es', '{{}}', 'sh5');", True)

    test(port, "Write private/stephane ✓", "owner", "priv_panini_2026",
         f"USE {db}; CALL DOLT_CHECKOUT('private/stephane'); "
         f"INSERT INTO user_files (file_hash, file_path, file_name, file_size, owner) "
         f"VALUES ('aclh6', '/z', 'z.txt', 30, 'stephane');", True)

    test(port, "Create private/test_acl ✓", "owner", "priv_panini_2026",
         f"USE {db}; CALL DOLT_BRANCH('private/test_acl');", True)

    # ── GROUP 4: namespace control ───────────────────────────
    print("\n🔒 Namespace control (branch creation)")
    print("-" * 50)

    test(port, "public_user → private/hack ✗", "public_user", "pub_panini_2026",
         f"USE {db}; CALL DOLT_BRANCH('private/hack');", False)

    test(port, "analyst → private/hack2 ✗", "analyst", "conf_panini_2026",
         f"USE {db}; CALL DOLT_BRANCH('private/hack2');", False)

    # ── CLEANUP ──────────────────────────────────────────────
    print("\n🧹 Cleanup")
    print("-" * 50)
    cleanup_sql = f"""
USE {db};
CALL DOLT_CHECKOUT('main');
DELETE FROM public_statistics WHERE stat_type LIKE 'acl_%';
CALL DOLT_CHECKOUT('confidential');
DELETE FROM semantic_mappings WHERE content_hash LIKE 'aclh%';
CALL DOLT_CHECKOUT('private/stephane');
DELETE FROM user_files WHERE file_hash LIKE 'aclh%';
CALL DOLT_CHECKOUT('main');
CALL DOLT_BRANCH('-D', 'private/test_acl');
"""
    mysql_cmd(port, "root", "", cleanup_sql)
    print("  ✅ Test data cleaned up")

    # ── SUMMARY ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    passed = sum(1 for _, _, p in RESULTS if p)
    total = len(RESULTS)
    pct = 100 * passed // total if total else 0
    print(f"RESULTS: {passed}/{total} tests passed ({pct}%)")
    print("-" * 70)
    for name, status, _ in RESULTS:
        print(f"  {status} {name}")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED — Dolt Branch ACL isolation verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Test Dolt Branch ACL isolation")
    parser.add_argument("--port", type=int, default=3306, help="Dolt server port")
    args = parser.parse_args()
    sys.exit(run_tests(args.port))


if __name__ == "__main__":
    main()
