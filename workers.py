import sqlite3, threading, time, uuid
from contextlib import closing

class Workers:
    def __init__(self, path, invoke):
        self.path, self.invoke = path, invoke
        self.stop = threading.Event()
        with closing(self.db()) as c, c:
            c.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, role TEXT, mission TEXT, status TEXT, result TEXT, created REAL)")
    def db(self):
        return sqlite3.connect(self.path, timeout=15)
    def submit(self, role, mission):
        if not role.strip() or not mission.strip() or len(mission)>8000:
            raise ValueError("Invalid worker mission")
        ident=uuid.uuid4().hex
        with closing(self.db()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            if c.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]>=20:
                raise RuntimeError("Worker queue full")
            c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?)",(ident,role[:100],mission,"queued","",time.time()))
        return ident
    def list(self):
        with closing(self.db()) as c:
            return c.execute("SELECT id,role,status,result FROM jobs ORDER BY created DESC LIMIT 30").fetchall()
    def step(self):
        with closing(self.db()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT id,role,mission FROM jobs WHERE status='queued' ORDER BY created LIMIT 1").fetchone()
            if not row: return False
            c.execute("UPDATE jobs SET status='running' WHERE id=?",(row[0],))
        try:
            result=self.invoke(row[1],row[2])
            status="completed"
        except Exception as e:
            result=type(e).__name__
            status="failed"
        with closing(self.db()) as c, c:
            c.execute("UPDATE jobs SET status=?,result=? WHERE id=?",(status,str(result)[:16000],row[0]))
        return True
    def start(self):
        with closing(self.db()) as c, c:
            c.execute("UPDATE jobs SET status='interrupted' WHERE status='running'")
        def loop():
            while not self.stop.is_set():
                try:
                    if not self.step(): self.stop.wait(2)
                except sqlite3.Error:
                    self.stop.wait(5)
        threading.Thread(target=loop,daemon=True,name="jarvis-worker").start()
