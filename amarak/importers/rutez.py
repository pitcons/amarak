# encoding: utf8
from store import Store
import sqlite3

def import_rutez():
    store = Store()
    store.ensure_thesaurus('rutez', u'РуТез')
    store.select('rutez')

    conn = sqlite3.connect('/home/petr/ownCloud/projects/rutez/rutez.db')
    c = conn.cursor()
    memd = {}
    c.execute("""select w1.name, w2.name, rel.name from rel
                 join sinset w1 on w1.id = rel.id
                 join sinset w2 on w2.id = rel.link
              """)
    store.set_autocommit(False)
    for row in c.fetchall():
        store.ensure_link(row[0], row[1], row[2])
        #print row[0], row[1], row[2]

    c.execute("""select s.name, w.name from sinset s
                 join word w on w.id = s.id
              """)
    for row in c.fetchall():
        store.ensure_word(row[0], row[1])

    store.commit()
#import_rutez()
