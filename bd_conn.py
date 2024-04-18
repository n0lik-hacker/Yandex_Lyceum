import sqlite3, traceback, random


class Quests:
    def __init__(self):
        self.author = 'hurmmaa'
        self.code = 0

    def create_quest(self, text, answer, prize, is_offical, author, chat_id, channels, description):
        con = sqlite3.connect("dark_bd.db")
        code = random.randint(100000, 999999)
        self.code = code
        self.author = author
        print(code)
        cur = con.cursor()
        cur.execute(f"""INSERT INTO quests(text, answer, prize, code, is_offical, author, chat_id, channels, description)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (text, answer, prize, code, is_offical, author, chat_id, channels, description))
        con.commit()
        con.close()

    def find_quest_id(self):
        con = sqlite3.connect("dark_bd.db")
        print(self.code)
        cur = con.cursor()
        n_id = cur.execute(f"""SELECT id_user FROM quests
                WHERE code = ? AND author = ?""", (self.code, self.author)).fetchone()
        con.commit()
        con.close()
        return n_id

    def get_chat_id(self, id):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        answered = cur.execute(f"""SELECT chat_id FROM quests
                                WHERE id_user = ?""", (id,)).fetchone()
        con.commit()
        con.close()
        return answered[0]

    def change_is_answered(self, id):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE quests SET is_answered = 1 WHERE id_user = {id}""")
        con.commit()
        con.close()

    def is_answered(self, id):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        answered = cur.execute(f"""SELECT is_answered FROM quests
                        WHERE id_user = ?""", (id,)).fetchone()
        con.commit()
        con.close()
        return answered[0]

    def get_is_offical_quests(self):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        quests = cur.execute(
            '''SELECT id_user, text, prize FROM quests WHERE is_offical = 1 and is_answered IS NULL''')
        ls = [i for i in quests]
        con.commit()
        con.close()
        if ls:
            return ls
        return False

    def give_quest(self, n_id):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        quest_inf = cur.execute(f"""SELECT text, answer, prize, code, author, description FROM quests
        WHERE id_user = ?""", (n_id,)).fetchone()
        con.close()
        return quest_inf

    def get_channels(self, id):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        answered = cur.execute(f"""SELECT channels FROM quests
                                WHERE id_user = ?""", (id,)).fetchone()
        if answered[0]:
            return [i.split() for i in answered[0].split('\n')]
        else:
            return False

    def get_user_quests(self, user_name):
        con = sqlite3.connect("dark_bd.db")
        cur = con.cursor()
        quests = cur.execute(
            '''SELECT id_user, text, prize FROM quests WHERE author = ? and is_answered IS NULL''', (user_name,))
        ls = [i for i in quests]
        con.commit()
        con.close()
        if ls:
            return ls
        return False
