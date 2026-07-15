import psycopg2

class StudentRepository:
    def get_connection(self):
        return psycopg2.connect(
            host="postgres",
            database="users",
            user="postgres",
            password="postgres"
        )

    def get_students(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM students")
        students = cur.fetchall()

        cur.close()
        conn.close()

        return students