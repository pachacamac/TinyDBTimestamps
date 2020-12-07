from datetime import datetime, timezone
from tinydb.middlewares import Middleware

class TimestampsMiddleware(Middleware):
  """Automatically handle timestamps in TinyDB"""

  def __init__(self,
                storage_cls,
                created_key='created_at',
                updated_key='updated_at',
                ts_func=(lambda: datetime.utcnow().replace(tzinfo=timezone.utc).isoformat())
              ):
    super().__init__(storage_cls)
    self.created_key = created_key
    self.updated_key = updated_key
    self.ts_func = ts_func
    self.previous_data = None

  def write(self, data):
    self.previous_data = self.previous_data or self.storage.read() or {}
    for table_name in data:
      table = data[table_name]
      ptable = self.previous_data.get(table_name, {})
      for doc_id in table:
        ts = self.ts_func()
        doc = table[doc_id]
        pdoc = ptable.get(doc_id, {})
        self.previous_data[table_name] = self.previous_data.get(table_name, {})
        # always write created_at either initially or from pdata so it can not be changed once set
        if self.created_key:
          doc[self.created_key] = pdoc.get(self.created_key, ts)
          # TODO: is this enough of a copy for all cases?
          self.previous_data[table_name][doc_id] = dict(doc)
        if self.updated_key and ((self.updated_key not in doc) or (doc != pdoc)): # updated entry
          doc[self.updated_key] = ts
          # TODO: is this enough of a copy for all cases?
          self.previous_data[table_name][doc_id] = dict(doc)
    self.storage.write(data)
