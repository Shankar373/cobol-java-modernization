import os
import shutil
import sqlite3
from cobol_migrate import logical_indexed_compare, find_indexed_layout, decode_sqlite_records, dump_indexed_records, compare_logical_records

def test_logical_comparator_verification():
    import pytest
    from cobol_migrate import docker_available
    if not docker_available():
        pytest.skip("Docker is not available, skipping logical comparator verification test")

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo = os.path.join(ROOT, "legacy")
    discover_data = {
        "file_assigns": {
            "src/CCLOAD01.cob": [
                {
                    "assign_path": "data/work/customer.dat",
                    "logical_name": "CUSTOMER-MASTER",
                    "organization": "indexed"
                },
                {
                    "assign_path": "data/work/policy.dat",
                    "logical_name": "POLICY-MASTER",
                    "organization": "indexed"
                }
            ]
        },
        "copybook_dirs": ["copybooks"]
    }
    
    baseline_dir = os.path.join(ROOT, "target", "baseline", "legacy")
    results_dir = os.path.join(ROOT, "target", "results", "java")
    
    # 1. Verify files exist
    cust_baseline = os.path.join(baseline_dir, "data/work/customer.dat")
    cust_java = os.path.join(results_dir, "data/work/customer.dat")
    
    assert os.path.isfile(cust_baseline), "Baseline customer.dat missing"
    assert os.path.isfile(cust_java), "Java customer.dat missing"
    
    # Backup Java customer.dat to allow mutation safety
    cust_java_bak = cust_java + ".bak"
    shutil.copy2(cust_java, cust_java_bak)
    
    try:
        # Load schema
        schema = find_indexed_layout(repo, discover_data, "data/work/customer.dat")
        assert schema is not None, "Schema parsing failed for customer.dat"
        
        # A. Positive case: run logical compare and check verdict
        res = logical_indexed_compare(cust_baseline, cust_java, "data/work/customer.dat", repo, discover_data, baseline_dir)
        print("\n=== POSITIVE CASE EVIDENCE ===")
        print(f"res dict: {res}")
        assert res["verdict"] == "LOGICAL_MATCH", f"Expected LOGICAL_MATCH, got: {res.get('reason')}"
        
        # B. Negative mutation case: modify field value
        print("\n=== NEGATIVE CASE 1: MUTATED FIELD VALUE ===")
        conn = sqlite3.connect(cust_java)
        # Select first record to mutate
        row = conn.execute("SELECT key, value FROM table0 LIMIT 1").fetchone()
        orig_key = row[0]
        orig_val = bytearray(row[1])
        
        # Mutate value (offset 12 is Cust Name first char)
        orig_val[12] = ord('X')
        conn.execute("UPDATE table0 SET value = ? WHERE key = ?", (bytes(orig_val), orig_key))
        conn.commit()
        conn.close()
        
        res_mut = logical_indexed_compare(cust_baseline, cust_java, "data/work/customer.dat", repo, discover_data, baseline_dir)
        print(f"Mutated Verdict: {res_mut['verdict']}")
        print(f"Differences details: {res_mut.get('diffs')}")
        assert res_mut["verdict"] == "LOGICAL_MISMATCH", "Failed to detect mutated field value"
        
        # C. Missing record mutation: delete a record
        print("\n=== NEGATIVE CASE 2: MISSING RECORD ===")
        shutil.copy2(cust_java_bak, cust_java)
        
        conn = sqlite3.connect(cust_java)
        conn.execute("DELETE FROM table0 WHERE key = (SELECT key FROM table0 LIMIT 1)")
        conn.commit()
        conn.close()
        
        res_miss = logical_indexed_compare(cust_baseline, cust_java, "data/work/customer.dat", repo, discover_data, baseline_dir)
        print(f"Missing Record Verdict: {res_miss['verdict']}")
        print(f"Missing keys: {res_miss.get('missing_keys')}")
        assert res_miss["verdict"] == "LOGICAL_MISMATCH", "Failed to detect missing record"
        
        # D. Extra record mutation: add a dummy record
        print("\n=== NEGATIVE CASE 3: EXTRA RECORD ===")
        shutil.copy2(cust_java_bak, cust_java)
        
        conn = sqlite3.connect(cust_java)
        row = conn.execute("SELECT value FROM table0 LIMIT 1").fetchone()
        conn.execute("INSERT INTO table0 (key, value) VALUES (?, ?)", (b"999999", row[0]))
        conn.commit()
        conn.close()
        
        res_extra = logical_indexed_compare(cust_baseline, cust_java, "data/work/customer.dat", repo, discover_data, baseline_dir)
        print(f"Extra Record Verdict: {res_extra['verdict']}")
        print(f"Extra keys: {res_extra.get('extra_keys')}")
        assert res_extra["verdict"] == "LOGICAL_MISMATCH", "Failed to detect extra record"
        
    finally:
        shutil.copy2(cust_java_bak, cust_java)
        if os.path.exists(cust_java_bak):
            os.remove(cust_java_bak)
        print("\n=== CLEANUP COMPLETE ===")
