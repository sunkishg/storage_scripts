import sqlite3

conn = sqlite3.connect('nas_exceeded_fs.sqlite')
cur = conn.cursor()

nas_fs = { }

cur.executescript("""
DROP TABLE IF EXISTS storage_vendor;
DROP TABLE IF EXISTS storage_array;
DROP TABLE IF EXISTS nas_filesystem;

CREATE TABLE IF NOT EXISTS storage_vendor (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    array_vendor TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS storage_array (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    array_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS nas_filesystem (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    storage_vendor_id INTEGER,
    storage_array_id INTEGER,
    filesystem TEXT UNIQUE,
    totalspace TEXT,
    usedspace TEXT,
    availablespace TEXT,
    filesystemcapacity TEXT,
    totalinodes TEXT,
    usedinodes TEXT,
    availableinodes TEXT,
    inodecapacity TEXT
);
""")

for vendor, filerdata in sorted(nas_fs.items()):
    cur.execute('''INSERT OR IGNORE INTO storage_vendor (array_vendor)
        VALUES ( ? )''', ( vendor, ) )
    cur.execute('SELECT id FROM storage_vendor WHERE array_vendor = ? ', (vendor, ))
    storage_vendor_id = cur.fetchone()[0]

    for array, voldata in sorted(filerdata.items()):
        cur.execute('''INSERT OR IGNORE INTO storage_array (array_name)
            VALUES ( ? )''', ( array, ) )
        cur.execute('SELECT id FROM storage_array WHERE array_name = ? ', (array, ))
        storage_array_id = cur.fetchone()[0]

        for filesystem, value in sorted(voldata.items()):
            cur.execute('''INSERT OR REPLACE INTO nas_filesystem
                (storage_vendor_id, storage_array_id, filesystem, totalspace, usedspace, availablespace, filesystemcapacity, totalinodes, usedinodes, availableinodes, inodecapacity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (storage_vendor_id, storage_array_id, filesystem,value['total_space'],value['used_space'],value['avail_space'],value['fs_capacity'],value['itotal'],value['iused'],value['ifree'],value['i_capacity']))
            conn.commit()


# cur.execute("""SELECT * FROM nas_filesystem WHERE filesystemcapacity > 90 OR inodecapacity > 90""")
# for row in cur.fetchall():
#     print(row)

cur.execute('''
SELECT storage_vendor.array_vendor, storage_array.array_name, nas_filesystem.filesystem, nas_filesystem.totalspace, nas_filesystem.usedspace, nas_filesystem.availablespace, nas_filesystem.filesystemcapacity, nas_filesystem.totalinodes, nas_filesystem.usedinodes, nas_filesystem.availableinodes, nas_filesystem.inodecapacity
FROM nas_filesystem JOIN storage_vendor JOIN storage_array
    ON nas_filesystem.storage_vendor_id = storage_vendor.id AND nas_filesystem.storage_array_id = storage_array.id 
    where nas_filesystem.filesystemcapacity > 90 LIMIT 3
    ORDER BY nas_filesystem.filesystemcapacity > 90 LIMIT 3
''')
output_data = cur.fetchall()
print(output_data)
cur.close()
conn.close()

