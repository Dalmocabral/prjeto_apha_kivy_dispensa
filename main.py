from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from datetime import datetime
from models import session, User

class UserList(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.refresh_users()

    def refresh_users(self):
        self.clear_widgets()
        users = session.query(User).order_by(
            User.afastado.asc(),
            User.dataDispensa.asc().nullsfirst()
        ).all()

        for user in users:
            user_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            user_box.add_widget(Label(text=str(user.id), size_hint_x=0.1))
            user_box.add_widget(Label(text=user.name, size_hint_x=0.3))
            
            afastado_checkbox = CheckBox(size_hint_x=0.1)
            afastado_checkbox.active = user.afastado
            afastado_checkbox.bind(on_release=lambda chk, user=user: self.toggle_afastado(user))
            user_box.add_widget(afastado_checkbox)

            dispensa_button = Button(text='Dispensa', size_hint_x=0.2)
            dispensa_button.bind(on_press=lambda btn, user=user: self.dispensa(user))
            user_box.add_widget(dispensa_button)

            self.add_widget(user_box)

    def toggle_afastado(self, user):
        user.afastado = not user.afastado
        session.commit()
        self.refresh_users()

    def dispensa(self, user):
        user.dataDispensa = datetime.utcnow()
        session.commit()
        self.refresh_users()

class DispensaApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical')
        self.user_input = TextInput(hint_text='Nome do Usuário', size_hint_y=None, height=50)
        add_user_button = Button(text='Adicionar Usuário', size_hint_y=None, height=50)
        add_user_button.bind(on_press=lambda _: self.add_user(self.user_input.text))
        main_layout.add_widget(self.user_input)
        main_layout.add_widget(add_user_button)
        main_layout.add_widget(UserList())
        copy_btn = Button(text='Copiar para WhatsApp', size_hint_y=None, height=50)
        copy_btn.bind(on_press=self.copy_to_clipboard)
        main_layout.add_widget(copy_btn)
        return main_layout

    def add_user(self, user_name):
        if user_name.strip():
            new_user = User(name=user_name)
            session.add(new_user)
            session.commit()
            self.root.children[1].refresh_users()
            self.user_input.text = ''

    def copy_to_clipboard(self, instance=None):
        users = session.query(User).filter_by(afastado=False).all()
        date_str = datetime.now().strftime('%d/%m/%Y')
        text = f'*DISPENSA ATUALIZADA* {date_str}\n\n'
        for idx, user in enumerate(users, start=1):
            text += f'*{idx}* - _{user.name}_\n'
        Clipboard.copy(text)
        print('Texto copiado para a área de transferência')

if __name__ == '__main__':
    DispensaApp().run()
