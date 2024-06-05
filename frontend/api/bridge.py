import httpx

# Паттерн Мост, который реализует соединение с API

TIMEOUT = 10.0

class IReader:
    def __init__(self):
        self.host = "http://127.0.0.1:8000/"
        self.curr_user_id = 0


class HTTPXReader(IReader):
    def user_signup(self, email: str, password: str):
        r = httpx.post(self.host + "users/signup/", json={"email": email, "password": password}, timeout=TIMEOUT)
        self.curr_user_id = r.json().get("id")
        return r.json()

    def user_login(self, email: str, password: str):
        r = httpx.post(self.host + "users/login/", json={"email": email, "password": password}, timeout=TIMEOUT)
        self.curr_user_id = r.json().get("id")
        return r.json()

    def create_note(self, title: str, content: str):
        r = httpx.post(self.host + "notes/create/", json={"title": title, "content": content, "owner_id": self.curr_user_id}, timeout=TIMEOUT)
        return r.json()

    def get_user_notes(self):
        r = httpx.get(self.host + f"notes/{self.curr_user_id}", timeout=TIMEOUT)
        return r.json()

    def reverse_note_status(self, note_id: int):
        r = httpx.post(self.host + f"notes/done/", json={"note_id": note_id}, timeout=TIMEOUT)
        return r.json()


if __name__ == "__main__":
    reader = HTTPXReader()
    print(reader.user_login("test@test", "test"))
    print(reader.get_user_notes())
    # print(reader.create_note(title="test2", content="test2"))