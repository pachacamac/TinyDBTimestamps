# TinyDBTimestamps

Timestamps Middleware for TinyDB

Please note that this is not optimized for performance


## Usage:

  ### simple example:
    import TimestampsMiddleware
    from tinydb import TinyDB
    from tinydb.storages import MemoryStorage

    with TinyDB(storage=TimestampsMiddleware(MemoryStorage)) as db:
      db.insert({"foo": "bar"})
      for doc in db:
        print(doc)

  ### extended example:
    import TimestampsMiddleware
    from tinydb import TinyDB, where
    from tinydb.storages import JSONStorage
    import time

    store = TimestampsMiddleware(
      JSONStorage,
      created_key=None,
      updated_key="mtime",
      ts_func=time.time
    )
    with TinyDB('db.json', storage=store) as db:
      table = db.table('test')
      table.insert({"foo": "bar", "num": 123})
      table.insert({"foo": "bar", "num": 456})
      table.update({"num": 42}, where("num") == 456)
      for doc in table:
        print(doc)


## Tips/Notes

* will not let you override the defined timestamp keys
* you can skip the created key or updated key by setting it to None
* you can define your own timestamp function by setting ts_func