# -*- coding: utf-8
import pprint

from pywebio import start_server
from pywebio.output import put_table, put_tabs, put_markdown, put_link, put_widget, put_button, put_text
from pywebio.input import input, input_group, TEXT, PASSWORD, actions, textarea
from frontend.api.bridge import HTTPXReader

reader = HTTPXReader()

global_notes = []

# Паттерн Цепочка связностей

class IWorker():
    def set_next_worker(self, worker: 'IWorker') -> 'IWorker':
        pass

    def execute(self, command: str) -> str:
        pass


class AbsWorker(IWorker):
    def __init__(self):
        self.__next_worker: IWorker = None

    def set_next_worker(self, worker: 'IWorker') -> 'IWorker':
        self.__next_worker = worker
        return worker

    def execute_next(self, command: str) -> str:
        self.__next_worker.execute(command=command)

    def execute(self, command: str) -> str:
        if self.__next_worker is not None:
            return self.__next_worker.execute(command)
        return ''


class IWidget:
    def render(self):
        pass


class Note(IWidget):
    def __init__(self, _id: int, title: str, contents: str, done: bool = False):
        self._id = _id
        self._tpl = '''
        <details {{#open}}open{{/open}}>
            <summary>{{title}}</summary>
            {{#contents}}
                {{& pywebio_output_parse}}
            {{/contents}}
        </details>
        '''
        self.title = title
        self.contents = contents
        self.done = done

    def render(self):
        return put_widget(self._tpl, {
            "open": False,
            "title": self.title + f"{' (Done)' if self.done else ''}",
            "contents": [
                put_markdown(self.contents),
                # actions('', ["Done" if not self.done else "Not done", "Delete"]),
                put_button("Done" if not self.done else "Not done", onclick=lambda: reader.reverse_note_status(self._id)),
                put_button("Delete", onclick=lambda: self.done)
            ]
        })


class Dashboard(AbsWorker):
    def execute(self, command: str) -> str:
        if command == 'start':
            notes = []
            print(reader.curr_user_id)
            api_notes = reader.get_user_notes()
            for api_note in api_notes:
                notes.append(Note(
                    _id=api_note["id"],
                    title=api_note["title"],
                    contents=api_note["content"],
                    done=api_note["done"]
                ))

            global global_notes
            global_notes = notes

            put_tabs([{'title': note.title, 'content': note.render()} for note in notes])
            print("Notes to be displayed in tabs:", notes)
            data = input_group("Add new note", [
                input("Title", name="title", type=TEXT),
                textarea("Content", name="content", type=TEXT)
            ])
            reader.create_note(data['title'], data['content'])
            return "done"


class LoginPage(AbsWorker):
    def execute(self, command: str) -> str:
        if command == 'start':
            data = input_group("Shared TODO", [
                input("Email", name="email", type=TEXT),
                input("Password", name="password", type=PASSWORD),
                actions('', ["Login", "Sign up"], name="action_btn")
            ])
            if data["action_btn"] == "Login":
                reader.user_login(email=data["email"], password=data["password"])
                self.execute_next('start')
            elif data["action_btn"] == "Sign up":
                reader.user_signup(email=data["email"], password=data["password"])

            put_tabs(global_notes)

            return command
        if command == 'dashboard':
            put_tabs(global_notes)
            return "dashboard"


def give_command(worker: IWorker, command: str):
    string: str = worker.execute(command)
    if string == '':
        print(command + '- there is no performer')
    else:
        print(string)


def main():
    login_page = LoginPage()
    dashboard = Dashboard()
    login_page.set_next_worker(dashboard)

    reader.user_login("test@test.com", "test")

    give_command(login_page, 'start')


if __name__ == '__main__':
    start_server(main, port=8080)
