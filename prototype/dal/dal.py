import sqlite3 as sq

#region sql code
def get_user(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM users WHERE login=?", [log])
        r = cur.fetchone()
        return r

def get_user_by_position(message, city):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM users WHERE role=? AND campus=? ORDER BY rating DESC", [log, city])
        r = cur.fetchall()
        return r

def get_object(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM objects WHERE name=?", [log])
        r = cur.fetchone()
        return r

def get_object_by_id(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM objects WHERE rowid=?", [log])
        r = cur.fetchone()
        return r

def get_booking_by_id(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM bookings WHERE rowid=?", [log])
        r = cur.fetchone()
        return r

def get_object_by_type(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM objects WHERE type=?", [log])
        r = cur.fetchall()
        return r

def get_book_by_id(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM objects WHERE book_id=?", [log])
        r = cur.fetchone()
        return r

def get_book_by_userid(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = message
        cur.execute("SELECT rowid, * FROM bookings WHERE user_id=?", [log])
        r = cur.fetchall()
        return r

def remove_booking_by_id(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = message
        cur.execute("DELETE FROM bookings WHERE rowid=?", [log])


def get_book_by_available_for_students(message, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = message
        cur.execute("SELECT rowid, * FROM objects WHERE available_for_students=? AND campus=?", [log, position])
        r = cur.fetchall()
        return r

def get_book_by_available_for_abiturients(message, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = message
        cur.execute("SELECT rowid, * FROM objects WHERE available_for_abiturients=? AND campus=?", [log, position])
        r = cur.fetchall()
        return r

def get_book_by_id(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        log = str(message)
        cur.execute("SELECT rowid, * FROM objects WHERE book_id=?", [log])
        r = cur.fetchone()
        return r

def getbookr(obj_id, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        time_campus = get_time(position)
        cur.execute("SELECT bookings.rowid, timestart, timefinish, users.login "
                    "FROM bookings JOIN objects JOIN users ON bookings.object_id = objects.rowid "
                    "AND bookings.user_id = users.rowid WHERE bookings.object_id = ? "
                    "AND bookings.timefinish > ?", [obj_id, time_campus])
        r = cur.fetchall()
        return r


def getlast(us_id, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        time_campus = get_time(position)
        cur.execute("SELECT bookings.rowid, timestart, timefinish, users.login, bookings.object_id, objects.name "
                    "FROM bookings JOIN objects JOIN users ON bookings.object_id = objects.rowid "
                    "AND bookings.user_id = users.rowid WHERE bookings.user_id = ? "
                    "AND bookings.timestart < ? LIMIT 10", [us_id, time_campus])
        r = cur.fetchall()
        return r


def get_users_bookings(us_id, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        time_campus = get_time(position)
        cur.execute("SELECT bookings.rowid, timestart, timefinish, users.login, bookings.object_id, objects.name "
                    "FROM bookings JOIN objects JOIN users ON bookings.object_id = objects.rowid "
                    "AND bookings.user_id = users.rowid WHERE bookings.user_id = ? "
                    "AND bookings.timefinish > ?", [us_id, time_campus])
        r = cur.fetchall()
        return r


def getlogs(obj_id, position):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        time_campus = get_time(position)
        cur.execute("SELECT bookings.rowid, timestart, timefinish, users.login, bookings.object_id, objects.name "
                    "FROM bookings JOIN objects JOIN users ON bookings.object_id = objects.rowid "
                    "AND bookings.user_id = users.rowid WHERE bookings.object_id = ? "
                    "LIMIT 10", [obj_id])
        r = cur.fetchall()
        return r

def get_time(position):
    with sq.connect("db.db") as con:
        con.row_factory = sq.Row
        cur = con.cursor()
        if position == "nsk":
            time_campus = "+7 hour"
        else:
            time_campus = "+3 hour"
        cur.execute("SELECT datetime('now', ?) as datetime", [time_campus])
        r = cur.fetchone()['datetime']
        return r

def count_games():
    with sq.connect("db.db") as con:
        con.row_factory = sq.Row
        cur = con.cursor()
        cur.execute("SELECT count(type) as count FROM objects WHERE type = 'game'")
        r = cur.fetchone()['count']
        return r

def get_all_games():
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM objects WHERE type = 'game'")
        r = cur.fetchall()
        return r

def get_all_active_reports():
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("SELECT rowid, * FROM reports WHERE status = 1")
        r = cur.fetchall()
        return r

def get_all_reports_by_user(name):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("SELECT rowid, * FROM reports WHERE user_login = ?", [name])
        r = cur.fetchall()
        return r

def check_valid_date(dsn):
    with sq.connect("db.db") as con:
        con.row_factory =sq.Row
        cur = con.cursor()
        cur.execute("SELECT datetime(?) as dt", [dsn])
        r = cur.fetchone()['dt']
        return r

def add_booking(us_id, dsn, dfn, obj_id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO bookings VALUES (?, ?, ?, ?)", [us_id, dsn, dfn, obj_id])


def add_report(us_log, dt, obj_name, rep_text):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO reports VALUES (?, ?, ?, ?, 1, '')", [us_log, dt, obj_name, rep_text])


def add_game(type, name, description, campus, count, book_id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO objects VALUES (?, ?, ?, '', ?, ?, 0, 0, ?)", [type, name, description, campus, count, book_id])


def change_change_inactive_report(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE reports SET status = 0 WHERE rowid = ?", [message.text])


def make_available_for_students(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE objects SET available_for_students = 1, available_for_abiturients = 0 WHERE name = ?", [message])


def make_available_for_abiturients(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE objects SET available_for_abiturients = 1, available_for_students = 0 WHERE name = ?", [message])

def sql_change_raiting(sum, message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET rating = ? WHERE login = ?", [sum, message])

def make_unvailable(message):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE objects SET available_for_abiturients = 0, available_for_students = 0 WHERE name = ?",
                    [message.text])

def validate_inventory_name(name):
    with sq.connect("db.db") as con:
        #con.row_factory = sq.Row
        cur = con.cursor()
        cur.execute("SELECT rowid as id FROM objects WHERE name = ?", [name])
        r = cur.fetchone()
        print(r)
        if r != None:
            return 0
        else:
            return 1

def upd_count_object(name, count):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        cur.execute("UPDATE objects SET count = count + ? WHERE name = ?", [count, name])
#endregion