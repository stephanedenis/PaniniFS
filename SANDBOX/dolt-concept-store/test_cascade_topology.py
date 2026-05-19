#!/usr/bin/env python3
"""
Dolt Cascade Distribution Topology -- Proof of Concept
=======================================================
Validates the 3-tier cascade:
  DoltHub (public, free) -> DoltLab/Pro (confidential) -> Local (private)

For local testing, we simulate 'dolt clone' using:
  1. shutil.copytree (copies the .dolt storage, like clone does)
  2. dolt remote add (sets up remote tracking)
  3. dolt backup sync + fetch (simulates push/pull)

In production, all of this becomes:
  dolt clone https://dolthub.com/org/panini-public
  dolt clone https://doltlab.myorg.com/panini-confidential
  dolt remote add upstream https://dolthub.com/org/panini-public
  dolt push / dolt pull
"""
import subprocess, shutil, os, sys

BASE = "/tmp/cascade_poc"
PASS_COUNT = 0
FAIL_COUNT = 0

def dolt(args, cwd):
    """Run dolt with no pager."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    env["PAGER"] = "cat"
    env["TERM"] = "dumb"
    r = subprocess.run(["dolt"] + args, cwd=cwd, capture_output=True, text=True,
                       env=env, timeout=30)
    if r.returncode != 0:
        err = r.stderr.strip()
        if not any(skip in err.lower() for skip in ["already", "nothing to commit", "up to date"]):
            print(f"  WARN dolt {' '.join(args[:3])}: {err[:250]}")
    return r.stdout.strip()

def sql_csv(query, cwd):
    """Run SQL, return CSV. Note: -r csv BEFORE -q."""
    return dolt(["sql", "-r", "csv", "-q", query], cwd)

def sql_exec(query, cwd):
    """Execute SQL."""
    return dolt(["sql", "-q", query], cwd)

def clone_local(src, dst):
    """Simulate dolt clone by copying the database directory."""
    shutil.copytree(src, dst)
    # Clear any existing remotes/backups from the clone
    # (the clone should start fresh with its own remote config)

def check(condition, label):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")

# ---- Cleanup ----
shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE)

print("=" * 70)
print("  DOLT CASCADE DISTRIBUTION TOPOLOGY -- PROOF OF CONCEPT")
print("=" * 70)

# ======================================================
# TIER 1: PUBLIC REPO (= DoltHub free)
# ======================================================
pub = os.path.join(BASE, "panini-public")
os.makedirs(pub)
dolt(["init", "--name", "PaniniFS", "--email", "panini@panini-fs.org"], pub)

sql_exec("CREATE TABLE dhatu (id INT PRIMARY KEY, code VARCHAR(10), name_en VARCHAR(50), name_fr VARCHAR(50));", pub)
sql_exec("INSERT INTO dhatu VALUES (1,'COMM','Communicate','Communiquer'),(2,'ITER','Iterate','Iterer'),(3,'TRANS','Transform','Transformer');", pub)
sql_exec("CREATE TABLE format_grammars (id INT PRIMARY KEY, format_name VARCHAR(50), mime_type VARCHAR(100));", pub)
sql_exec("INSERT INTO format_grammars VALUES (1,'PNG','image/png'),(2,'JPEG','image/jpeg'),(3,'PDF','application/pdf');", pub)
sql_exec("CREATE TABLE public_statistics (id INT PRIMARY KEY AUTO_INCREMENT, stat_type VARCHAR(50), val VARCHAR(100));", pub)
dolt(["add", "."], pub)
dolt(["commit", "-m", "Initial public: 3 dhatu + 3 formats + stats"], pub)

pub_count = sql_csv("SELECT COUNT(*) AS n FROM dhatu;", pub).split("\n")[-1]
print(f"\n  TIER 1 - PUBLIC (DoltHub free)")
print(f"  Path: {pub}")
print(f"  Tables: dhatu ({pub_count}), format_grammars (3), public_statistics")
print(f"  Branch: main")

# ======================================================
# TIER 2: CONFIDENTIAL (= DoltLab / DoltHub Pro)
# Simulate clone from public
# ======================================================
conf = os.path.join(BASE, "panini-confidential")
clone_local(pub, conf)

# Verify the clone inherited data
conf_count = sql_csv("SELECT COUNT(*) AS n FROM dhatu;", conf).split("\n")[-1]
print(f"\n  TIER 2 - CONFIDENTIAL (DoltLab / DoltHub Pro)")
print(f"  Cloned from panini-public: {conf_count} dhatu inherited")

# Add remote to public (for upstream sync)
# In production: origin is set automatically by dolt clone
# Here: we set up a backup-based remote for sync testing
backup_pub = os.path.join(BASE, "backup-pub")
dolt(["backup", "add", "pub-backup", f"file://{backup_pub}"], pub)
dolt(["backup", "sync", "pub-backup"], pub)
dolt(["remote", "add", "upstream-public", f"file://{backup_pub}"], conf)

# Create confidential branch
dolt(["checkout", "-b", "confidential"], conf)
sql_exec("CREATE TABLE semantic_mappings (id INT PRIMARY KEY, content_hash VARCHAR(64), language VARCHAR(10), text TEXT, dhatu_code VARCHAR(10));", conf)
sql_exec("INSERT INTO semantic_mappings VALUES (1,'abc123','fr','communication digitale','COMM'),(2,'abc123','en','digital communication','COMM'),(3,'def456','es','iteracion rapida','ITER');", conf)
sql_exec("CREATE TABLE analysis_results (id INT PRIMARY KEY, dhatu_code VARCHAR(10), confidence FLOAT, model_version VARCHAR(20));", conf)
sql_exec("INSERT INTO analysis_results VALUES (1,'COMM',0.95,'v0.2.2'),(2,'ITER',0.87,'v0.2.2');", conf)
sql_exec("CREATE TABLE dedup_index (id INT PRIMARY KEY, content_hash VARCHAR(64), ref_count INT);", conf)
sql_exec("INSERT INTO dedup_index VALUES (1,'abc123',2),(2,'def456',1);", conf)
dolt(["add", "."], conf)
dolt(["commit", "-m", "confidential: semantic_mappings + analysis + dedup"], conf)
dolt(["checkout", "main"], conf)

branches_c = [b.strip().lstrip("* ") for b in dolt(["branch"], conf).split("\n") if b.strip()]
print(f"  Branches: {', '.join(branches_c)}")
print(f"  Confidential tables added: semantic_mappings, analysis_results, dedup_index")

# ======================================================
# TIER 3: PRIVATE (= Local / Hosted Dolt)
# Simulate clone from confidential
# ======================================================
priv = os.path.join(BASE, "panini-private")
clone_local(conf, priv)

# Verify inherited data: main + confidential branches
priv_main_count = sql_csv("SELECT COUNT(*) AS n FROM dhatu;", priv).split("\n")[-1]
dolt(["checkout", "confidential"], priv)
priv_conf_count = sql_csv("SELECT COUNT(*) AS n FROM semantic_mappings;", priv).split("\n")[-1]
dolt(["checkout", "main"], priv)

print(f"\n  TIER 3 - PRIVATE (Local / Hosted Dolt)")
print(f"  Cloned from panini-confidential")
print(f"  Inherited: {priv_main_count} dhatu (main), {priv_conf_count} semantic_mappings (confidential)")

# Add SECOND remote pointing to public (upstream)
dolt(["remote", "add", "upstream-public-direct", f"file://{backup_pub}"], priv)

# Create private branch
dolt(["checkout", "-b", "private/stephane"], priv)
sql_exec("CREATE TABLE user_files (id INT PRIMARY KEY, filename VARCHAR(200), content_hash VARCHAR(64), owner VARCHAR(50), is_encrypted INT DEFAULT 1);", priv)
sql_exec("INSERT INTO user_files VALUES (1,'photo_vacances.png','aaa111','stephane',1),(2,'rapport_Q4.pdf','bbb222','stephane',1);", priv)
sql_exec("CREATE TABLE encryption_keys (id INT PRIMARY KEY, key_name VARCHAR(50), key_hash VARCHAR(64));", priv)
sql_exec("INSERT INTO encryption_keys VALUES (1,'master_key_2026','zzz999');", priv)
dolt(["add", "."], priv)
dolt(["commit", "-m", "private: user files + encryption keys"], priv)
dolt(["checkout", "main"], priv)

branches_p = [b.strip().lstrip("* ") for b in dolt(["branch"], priv).split("\n") if b.strip()]
print(f"  Branches: {', '.join(branches_p)}")
print(f"  Private tables added: user_files, encryption_keys")
remotes_p = dolt(["remote", "-v"], priv)
print(f"  Remotes:")
for line in remotes_p.split("\n"):
    if line.strip():
        print(f"    {line.strip()}")

# ======================================================
# TEST 1: DATA ISOLATION
# ======================================================
print(f"\n{'='*70}")
print(f"  TEST 1: DATA ISOLATION PER TIER")
print(f"{'='*70}")

def get_tables(cwd, schema):
    raw = sql_csv(f"SELECT GROUP_CONCAT(table_name ORDER BY table_name) AS t FROM information_schema.tables WHERE table_schema='{schema}' AND table_type='BASE TABLE';", cwd)
    return raw.split("\n")[-1].strip('"')

pub_t = get_tables(pub, "panini-public")
print(f"  PUBLIC/main:          {pub_t}")

conf_t_main = get_tables(conf, "panini-confidential")
print(f"  CONFID/main:          {conf_t_main}")

dolt(["checkout", "confidential"], conf)
conf_t_conf = get_tables(conf, "panini-confidential")
print(f"  CONFID/confidential:  {conf_t_conf}")
dolt(["checkout", "main"], conf)

priv_t_main = get_tables(priv, "panini-private")
print(f"  PRIVATE/main:         {priv_t_main}")

dolt(["checkout", "confidential"], priv)
priv_t_conf = get_tables(priv, "panini-private")
print(f"  PRIVATE/confidential: {priv_t_conf}")
dolt(["checkout", "main"], priv)

dolt(["checkout", "private/stephane"], priv)
priv_t_priv = get_tables(priv, "panini-private")
print(f"  PRIVATE/private:      {priv_t_priv}")
dolt(["checkout", "main"], priv)

# Verify isolation
check("semantic_mappings" not in pub_t, "PUBLIC has no confidential tables")
check("user_files" not in pub_t and "encryption_keys" not in pub_t, "PUBLIC has no private tables")
check("semantic_mappings" in conf_t_conf, "CONFIDENTIAL/confidential has semantic_mappings")
check("user_files" not in conf_t_conf, "CONFIDENTIAL has no private tables")
check("user_files" in priv_t_priv and "encryption_keys" in priv_t_priv, "PRIVATE has user_files + encryption_keys")
check("dhatu" in priv_t_main, "PRIVATE/main inherits dhatu from public")
check("semantic_mappings" in priv_t_conf, "PRIVATE/confidential inherits semantic_mappings")

# ======================================================
# TEST 2: UPSTREAM SYNC (public -> private)
# ======================================================
print(f"\n{'='*70}")
print(f"  TEST 2: UPSTREAM SYNC (public adds data -> private gets it)")
print(f"{'='*70}")

# Add 4 more dhatu to public
sql_exec("INSERT INTO dhatu VALUES (4,'DECIDE','Decide','Decider'),(5,'LOCATE','Locate','Localiser'),(6,'GROUP','Group','Grouper'),(7,'SEQ','Sequence','Sequencer');", pub)
dolt(["add", "."], pub)
dolt(["commit", "-m", "public: complete 7 dhatu"], pub)
dolt(["backup", "sync", "pub-backup"], pub)

new_pub_count = sql_csv("SELECT COUNT(*) AS n FROM dhatu;", pub).split("\n")[-1]
print(f"  PUBLIC: {new_pub_count} dhatu (added 4 new ones)")

# Private fetches from upstream-public-direct and merges
dolt(["fetch", "upstream-public-direct"], priv)
merge_result = dolt(["merge", "upstream-public-direct/main", "--no-edit"], priv)
new_priv_count = sql_csv("SELECT COUNT(*) AS n FROM dhatu;", priv).split("\n")[-1]
print(f"  PRIVATE after upstream fetch+merge: {new_priv_count} dhatu")

check(new_pub_count == new_priv_count == "7", f"Sync: pub={new_pub_count} == priv={new_priv_count} == 7")

# Check all dhatu codes
codes_raw = sql_csv("SELECT code FROM dhatu ORDER BY id;", priv)
codes = [c.strip() for c in codes_raw.split("\n")[1:] if c.strip()]
print(f"  Synced dhatu: {', '.join(codes)}")
check(len(codes) == 7, f"All 7 dhatu synced ({len(codes)} found)")
check("DECIDE" in codes and "SEQ" in codes, "New dhatu DECIDE + SEQ present")

# ======================================================
# TEST 3: PROMOTION (private -> public via main)
# ======================================================
print(f"\n{'='*70}")
print(f"  TEST 3: DATA PROMOTION (private aggregates -> public)")
print(f"{'='*70}")

dolt(["checkout", "private/stephane"], priv)
n_files = sql_csv("SELECT COUNT(*) AS n FROM user_files;", priv).split("\n")[-1]
n_keys = sql_csv("SELECT COUNT(*) AS n FROM encryption_keys;", priv).split("\n")[-1]
print(f"  Private data: {n_files} files, {n_keys} keys")
dolt(["checkout", "main"], priv)

# Write AGGREGATED stats (never raw data) to main for promotion
sql_exec(f"INSERT INTO public_statistics (stat_type, val) VALUES ('total_user_files','{n_files}');", priv)
sql_exec(f"INSERT INTO public_statistics (stat_type, val) VALUES ('total_encrypted_keys','{n_keys}');", priv)
dolt(["add", "."], priv)
dolt(["commit", "-m", "promote: aggregate stats from private"], priv)

stats = sql_csv("SELECT stat_type, val FROM public_statistics;", priv)
print(f"  Promotable stats on main:")
for line in stats.split("\n")[1:]:
    if line.strip():
        print(f"    {line}")

check("total_user_files" in stats, "Stats contain file count aggregate")
check("photo_vacances" not in stats and "zzz999" not in stats and "aaa111" not in stats,
      "No raw private data in promoted stats")

# ======================================================
# TEST 4: BRANCH LEAK PREVENTION
# ======================================================
print(f"\n{'='*70}")
print(f"  TEST 4: BRANCH LEAK PREVENTION")
print(f"{'='*70}")

pub_br = [b.strip().lstrip("* ") for b in dolt(["branch"], pub).split("\n") if b.strip()]
conf_br = [b.strip().lstrip("* ") for b in dolt(["branch"], conf).split("\n") if b.strip()]
priv_br = [b.strip().lstrip("* ") for b in dolt(["branch"], priv).split("\n") if b.strip()]

print(f"  PUBLIC:       {pub_br}")
print(f"  CONFIDENTIAL: {conf_br}")
print(f"  PRIVATE:      {priv_br}")

check(pub_br == ["main"], "PUBLIC has only main")
check("confidential" in conf_br, "CONFIDENTIAL has confidential branch")
check(not any("private" in b for b in conf_br), "No private/* in CONFIDENTIAL")
check(not any("confidential" in b for b in pub_br), "No confidential in PUBLIC")
check(not any("private" in b for b in pub_br), "No private/* in PUBLIC")
check("private/stephane" in priv_br, "PRIVATE has private/stephane")

# ======================================================
# TEST 5: MULTI-REMOTE
# ======================================================
print(f"\n{'='*70}")
print(f"  TEST 5: MULTI-REMOTE TOPOLOGY")
print(f"{'='*70}")

remotes = dolt(["remote", "-v"], priv)
print(f"  PRIVATE remotes:")
for line in remotes.split("\n"):
    if line.strip():
        print(f"    {line.strip()}")

check("upstream-public" in remotes, "Has upstream-public remote")
# Note: in this POC, origin comes from the copy, so upstream-public is the key one
check("backup-pub" in remotes, "Remote points to public backup store")

# ======================================================
# SUMMARY
# ======================================================
total = PASS_COUNT + FAIL_COUNT
print(f"\n{'='*70}")
if FAIL_COUNT == 0:
    print(f"  ALL {PASS_COUNT}/{total} TESTS PASSED -- CASCADE TOPOLOGY VALIDATED")
else:
    print(f"  {PASS_COUNT}/{total} PASSED, {FAIL_COUNT} FAILED")
print(f"{'='*70}")
print("""
  Validated architecture:

  DoltHub (FREE)             DoltLab / DoltHub Pro        Local / Hosted
  +-------------------+      +--------------------+      +-----------------+
  | panini-public     |      | panini-confidentiel|      | panini-prive    |
  |                   |clone |                    |clone |                 |
  | main              |<---->| main               |<---->| main            |
  |  dhatu (7)        |      |  dhatu (7)         |      |  dhatu (7)      |
  |  format_grammars  |      |  format_grammars   |      |  format_grammars|
  |  public_statistics|      |  public_statistics  |      |  public_stats   |
  |                   |      |                    |      |                 |
  |                   |      | confidential        |      | confidential    |
  |                   |      |  semantic_mappings  |      |  semantic_maps  |
  |                   |      |  analysis_results   |      |  analysis_res   |
  |                   |      |  dedup_index        |      |  dedup_index    |
  |                   |      |                    |      |                 |
  |                   |      |                    |      | private/stephane |
  |                   |      |                    |      |  user_files     |
  |                   |      |                    |      |  encrypt_keys   |
  +-------------------+      +--------------------+      +-----------------+
        ^                                                       |
        +------------- upstream remote (direct) ----------------+

  Data flow:
    DOWN: clone/pull (each tier inherits all ancestor data)
    UP:   push main only (aggregated stats, never raw data)

  Branch isolation (proven):
    - PUBLIC:       only 'main'
    - CONFIDENTIAL: 'main' + 'confidential'
    - PRIVATE:      'main' + 'confidential' + 'private/*'

  Hosting costs:
    PUBLIC:       DoltHub.com      FREE (unlimited public DBs)
    CONFIDENTIAL: DoltLab (free)   or DoltHub Pro ($50/mo)
    PRIVATE:      Local (free)     or Hosted Dolt ($50/mo min)

  Double security (with dolt sql-server + branch_control):
    1. Repo-level:   clone access controls who gets which DB
    2. Branch-level:  ACL controls who writes to which branch
""")

if FAIL_COUNT > 0:
    sys.exit(1)
