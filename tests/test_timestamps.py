import unittest
from TimestampsMiddleware import TimestampsMiddleware
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb.operations import delete
import time

class TimestampsMiddlewareFunctionality(unittest.TestCase):  
  def test_create(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      db.insert_multiple([
        {"xyz": "foo", "num": 2},
        {"xyz": "bar", "num": 4},
        {"xyz": "xxx", "num": 8}
      ])
      for doc in db:
        assert('created_at' in doc)
        assert('updated_at' in doc)

  def test_update(self):
    #with TinyDB('/tmp/db.json', storage=TimestampsMiddleware(JSONStorage)) as db:
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      id = db.insert({"xyz": "foo"})
      assert(db.get(doc_id=id).get("created_at"))
      assert(db.get(doc_id=id).get("updated_at"))
      ts = db.get(doc_id=id).get("updated_at")
      time.sleep(0.001)
      db.update({"xyz": "bar"}, doc_ids=[id])
      nts = db.get(doc_id=id).get("updated_at")
      assert(ts != nts)

  def test_alternative_key_names(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage, created_key="ctime", updated_key="mtime")) as db:
      id = db.insert({"xyz": "foo"})
      doc = db.get(doc_id=id)
      assert(doc["ctime"])
      assert(doc["mtime"])

  def test_skip_created_key(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage, created_key=None)) as db:
      id = db.insert({"xyz": "foo"})
      doc = db.get(doc_id=id)
      assert(doc.get("created_at") is None)
      assert(doc.get("updated_at"))
  
  def test_skip_updated_key(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage, updated_key=None)) as db:
      id = db.insert({"xyz": "foo"})
      doc = db.get(doc_id=id)
      assert(doc.get("updated_at") is None)
      assert(doc.get("created_at"))

  def test_alternative_ts_func(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage, ts_func=(lambda: f"TS:{time.time()}"))) as db:
      id = db.insert({"xyz": "foo"})
      doc = db.get(doc_id=id)
      assert(doc["created_at"].startswith("TS:"))
      assert(doc["updated_at"].startswith("TS:"))
      assert(doc["created_at"] == doc["updated_at"])

  def test_can_not_delete_created_at_key(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      id = db.insert({"xyz": "foo"})
      ts = db.get(doc_id=id).get("created_at")
      assert(ts)
      db.update(delete("created_at"), doc_ids=[id])
      assert(db.get(doc_id=id).get("created_at") == ts)

  def test_can_not_override_created_at_key(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      id = db.insert({"xyz": "foo", "created_at": "shizzle"})
      ts = db.get(doc_id=id).get("created_at")
      assert(ts)
      assert(ts != "shizzle")
      db.update({"created_at": "bullcrap"}, doc_ids=[id])
      nts = db.get(doc_id=id).get("created_at")
      assert(nts == ts)

  def test_can_not_override_updated_at_key(self):
    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      id = db.insert({"xyz": "foo"})
      ts = db.get(doc_id=id).get("updated_at")
      assert(ts)
      db.update({"updated_at": "bullcrap"}, doc_ids=[id])
      nts = db.get(doc_id=id).get("updated_at")
      assert(nts)
      assert(nts != "bullcrap")


if __name__ == '__main__':
  unittest.main()