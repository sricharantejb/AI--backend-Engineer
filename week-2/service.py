from repository import StudentRepository

repo = StudentRepository()

def get_students():
    return repo.get_students()