"""多店铺改造迁移脚本（幂等）：给 inventory_items / inventory_logs / boxes 增加 store_id，
建立 stores 表并 seed 店铺1，将现有数据归到店铺1，并把唯一约束改为按店铺联合唯一。

执行：python3 migrate_multistore.py [db_path]
"""
import sqlite3
import sys
import os

db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "wbtools.db")
print(f"迁移数据库: {db_path}")
conn = sqlite3.connect(db_path)
cur = conn.cursor()


def col_exists(table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())


def table_exists(table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


# 1) stores 表 + seed 店铺1
if not table_exists("stores"):
    cur.execute("""CREATE TABLE stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        created_at DATETIME
    )""")
    print("  + 创建表 stores")
cur.execute("SELECT count(*) FROM stores")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO stores (name, created_at) VALUES ('店铺1', datetime('now'))")
    print("  + 插入 店铺1")

# 2) 加 store_id 列
for tbl in ("inventory_items", "inventory_logs", "boxes"):
    if not col_exists(tbl, "store_id"):
        cur.execute(f"ALTER TABLE {tbl} ADD COLUMN store_id INTEGER NOT NULL DEFAULT 1")
        print(f"  + {tbl}.store_id")
    cur.execute(f"UPDATE {tbl} SET store_id = 1 WHERE store_id IS NULL")
    cur.execute(f"CREATE INDEX IF NOT EXISTS ix_{tbl}_store_id ON {tbl}(store_id)")

# 3) 唯一约束改为按店铺联合唯一
cur.execute("DROP INDEX IF EXISTS ix_inventory_items_code")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_items_code_store ON inventory_items(code, store_id)")
print("  * inventory_items: (code, store_id) 联合唯一")

cur.execute("DROP INDEX IF EXISTS ix_boxes_box_code")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_boxes_box_code_store ON boxes(box_code, store_id)")
print("  * boxes: (box_code, store_id) 联合唯一")

# 非唯一 code/box_code 普通索引（供按编码查询）
cur.execute("CREATE INDEX IF NOT EXISTS ix_inventory_items_code ON inventory_items(code)")
cur.execute("CREATE INDEX IF NOT EXISTS ix_boxes_box_code ON boxes(box_code)")

conn.commit()

# 校验
cur.execute("SELECT count(*) FROM inventory_items WHERE store_id=1")
print(f"校验 -> inventory_items@店铺1: {cur.fetchone()[0]}")
cur.execute("SELECT count(*) FROM boxes WHERE store_id=1")
print(f"校验 -> boxes@店铺1: {cur.fetchone()[0]}")
cur.execute("SELECT count(*) FROM inventory_logs WHERE store_id=1")
print(f"校验 -> inventory_logs@店铺1: {cur.fetchone()[0]}")
cur.execute("SELECT id, name FROM stores ORDER BY id")
print("店铺列表:", cur.fetchall())
conn.close()
print("迁移完成 ✅")
