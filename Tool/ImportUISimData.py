import json
from bsddb3 import db as bsddb3
import pandas as pd
from pandas import DataFrame

def read_db():
    listing_db = bsddb3.DB()
    listing_db.open("listing.db", None, bsddb3.DB_HASH, bsddb3.DB_CREATE | bsddb3.DB_DIRTY_READ)
    cursor = listing_db.cursor()
    rec = cursor.first()

    list = []
    while rec:
        list.append(json.loads(rec[1].decode(), encoding="utf-8"))
        rec = cursor.next()

    print(len(listing_db))
    df = DataFrame(list)
    df.to_csv("listing.csv", encoding="utf-8", index=False)

def import_ui_sim_data():
    df = pd.read_csv("..\\UISimulation\\UISimMain.csv", encoding="utf-8")

    listing_db = bsddb3.DB()
    listing_db.open("listing.db", None, bsddb3.DB_HASH, bsddb3.DB_CREATE | bsddb3.DB_DIRTY_READ)

    for item in df.to_dict("records"):
        listing_id = str(item["listingId"]).encode()
        if not listing_db.get(listing_id):
            listing_db.put(listing_id, json.dumps(item, ensure_ascii=False))
    pass


def import_ui_data():
    df = pd.read_csv("..\\UI\\UIMain.csv", encoding="utf-8")

    listing_db = bsddb3.DB()
    listing_db.open("listing.db", None, bsddb3.DB_HASH, bsddb3.DB_CREATE | bsddb3.DB_DIRTY_READ)

    for item in df.to_dict("records"):
        listing_id = str(item["listingId"]).encode()
        if not listing_db.get(listing_id):
            listing_db.put(listing_id, json.dumps(item, ensure_ascii=False))

    df = pd.read_csv("..\\UI\\UIMain201808.csv", encoding="utf-8")
    for item in df.to_dict("records"):
        listing_id = str(item["listingId"]).encode()
        if not listing_db.get(listing_id):
            print(f"insert {listing_id}")
            listing_db.put(listing_id, json.dumps(item, ensure_ascii=False))
    pass


def import_auto_data():
    df = pd.read_csv("listingInfo.csv", encoding="utf-8")
    print(df.shape)

    listing_db = bsddb3.DB()
    listing_db.open("listing.db", None, bsddb3.DB_HASH, bsddb3.DB_CREATE | bsddb3.DB_DIRTY_READ)

    for item in df.to_dict("records"):
        listing_id = str(item["listingId"]).encode()
        if not listing_db.get(listing_id):
            listing_db.put(listing_id, json.dumps(item, ensure_ascii=False))

def main():
    import_auto_data()
    read_db()


if __name__ == "__main__":
    main()