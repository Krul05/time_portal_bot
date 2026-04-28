import os

import psycopg2

class DB_manager:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "history"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST", "db"),
                port=os.getenv("DB_PORT", "5432")
            )
        except:
            print("Подключение к серверу не удалось")

    def addMuseum(self, museum, cur):
        cur.execute("""
                INSERT INTO museum(name_museum, type_museum, map_url)
                VALUES (%s, %s, %s) 
                RETURNING id
            """, (museum.name_museum, museum.type, museum.map_url))
        return cur.fetchone()[0]
    def addCreator(self, creator, address, cur):
        cur.execute("""
            INSERT INTO person(name_person, contact)
            VALUES (%s, %s)
            RETURNING id
        """, (creator, address))
        return cur.fetchone()[0]
    def addQuest(self, quest, museum_id, creator_id, cur):
        cur.execute("""
            INSERT INTO quest(name_quest, discription, creator, museum, num_rating, dec_rating, rating)
            VALUES (%s, %s, %s, %s, 0, 0, 0)
            RETURNING id
        """, (quest.name_quest, quest.discription, creator_id, museum_id))
        return  cur.fetchone()[0]
    def addQuestions(self, questions_arr, quest_id, cur):
        cur = self.conn.cursor()
        for i in range(len(questions_arr)):
            cur.execute("""
                    INSERT INTO question(question, answer, quest)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (questions_arr[i].question, questions_arr[i].answer, quest_id))
    def get_quests(self):
        cur = self.conn.cursor()
        cur.execute("""
        SELECT id, name_quest, discription, rating FROM quest order by rating desc
        """)
        quests = cur.fetchall()
        cur.close()
        return quests
    def get_questions(self, id):
        cur = self.conn.cursor()
        cur.execute("""
                SELECT question, answer FROM question where quest = %s
                """, (id,))
        questions = cur.fetchall()
        cur.close()
        return questions
    def set_rating(self, rating, quest_id):
        cur = self.conn.cursor()
        cur.execute("""
                        SELECT num_rating, dec_rating FROM quest where id = %s
                        """, (quest_id,))
        resp = cur.fetchall()
        print(resp)
        num_rating = int(resp[0][0]) + int(rating)
        dec_rating = int(resp[0][1]) + 1
        cur.close()
        self.set_new_rating(num_rating, dec_rating, quest_id)
    def set_new_rating(self, num_rating, dec_rating, quest_id):
        cur = self.conn.cursor()
        cur.execute("""
                                UPDATE quest set num_rating = %s, dec_rating = %s,  rating = %s where id = %s
                                """, (num_rating, dec_rating, round(float(num_rating)/float(dec_rating), 2), quest_id))
        self.conn.commit()
        cur.close()