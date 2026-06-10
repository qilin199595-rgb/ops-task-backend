from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os

app = FastAPI()

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "tasks.db")

# 初始化数据库
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tid TEXT DEFAULT '',
            stage TEXT NOT NULL,
            goal TEXT NOT NULL,
            user TEXT DEFAULT '待填写',
            status TEXT DEFAULT '进行中',
            trigger TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # 写入示例数据（仅首次）
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        sample = [
            ('次日转化', '1197', '未付费用户', '激活', '新用户', '进行中', '未支付且首登48小时以上且未付费', ''),
            ('H5用户-连麦【付费-5分钟未转化】', '', '未付费用户', '转化', '快手渠道-新用户', '已结束', '首登48小时内收听解答后5分钟内未支付', ''),
            ('商店-连麦【免费转付费-3分钟】', '', '未付费用户', '转化', '商店渠道-新用户', '进行中', '免费连麦后3分钟未进行付费连麦', ''),
            ('小红书app用户促转化运营策略2', '1161', '未付费用户', '激活', '小红书渠道-新用户', '进行中', '首登后3分钟内未支付', ''),
        ]
        conn.executemany(
            "INSERT INTO tasks (name,tid,stage,goal,user,status,trigger,note) VALUES (?,?,?,?,?,?,?,?)",
            sample
        )
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 数据模型
class TaskIn(BaseModel):
    name: str
    tid: Optional[str] = ''
    stage: str
    goal: str
    user: Optional[str] = '待填写'
    status: Optional[str] = '进行中'
    trigger: Optional[str] = ''
    note: Optional[str] = ''

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    tid: Optional[str] = None
    stage: Optional[str] = None
    goal: Optional[str] = None
    user: Optional[str] = None
    status: Optional[str] = None
    trigger: Optional[str] = None
    note: Optional[str] = None

# API 路由
@app.get("/api/tasks")
def list_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/tasks")
def create_task(task: TaskIn):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tasks (name,tid,stage,goal,user,status,trigger,note) VALUES (?,?,?,?,?,?,?,?)",
        (task.name, task.tid, task.stage, task.goal, task.user, task.status, task.trigger, task.note)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="任务不存在")
    fields = {k: v for k, v in task.dict().items() if v is not None}
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", (*fields.values(), task_id))
        conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row)

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/tasks/batch")
def batch_import(tasks: list[TaskIn]):
    conn = get_db()
    added, updated = 0, 0
    for t in tasks:
        existing = conn.execute("SELECT id FROM tasks WHERE name=?", (t.name,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE tasks SET tid=?,stage=?,goal=?,user=?,status=?,trigger=?,note=? WHERE id=?",
                (t.tid, t.stage, t.goal, t.user, t.status, t.trigger, t.note, existing['id'])
            )
            updated += 1
        else:
            conn.execute(
                "INSERT INTO tasks (name,tid,stage,goal,user,status,trigger,note) VALUES (?,?,?,?,?,?,?,?)",
                (t.name, t.tid, t.stage, t.goal, t.user, t.status, t.trigger, t.note)
            )
            added += 1
    conn.commit()
    conn.close()
    return {"added": added, "updated": updated}

# 静态文件和首页
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
