from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.clipboard import Clipboard
from datetime import datetime
from models import User, session

class MenuScreen(Screen):
    pass

class AddUserScreen(Screen):
    pass

class UserListScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh_users()

    def refresh_users(self):
        self.ids.users_box.clear_widgets()
        users = session.query(User).order_by(
            User.afastado.asc(),
            User.dataDispensa.asc().nullsfirst()
        ).all()

        for idx, user in enumerate(users, start=1):
            user_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            user_box.add_widget(Label(text=str(idx), size_hint_x=0.1))
            user_box.add_widget(Label(text=user.name, size_hint_x=0.3))
            
            afastado_checkbox = CheckBox(size_hint_x=0.1)
            afastado_checkbox.active = user.afastado
            afastado_checkbox.bind(active=lambda checkbox, value, u=user: self.set_afastado(u, value))
            user_box.add_widget(afastado_checkbox)

            dispensa_button = Button(text='Dispensa', size_hint_x=0.2)
            dispensa_button.bind(on_press=lambda btn, u=user: self.dispensa_user(u))
            user_box.add_widget(dispensa_button)

            self.ids.users_box.add_widget(user_box)

    def set_afastado(self, user, value):
        user.afastado = value
        session.commit()
        self.refresh_users()

    def dispensa_user(self, user):
        user.dataDispensa = datetime.utcnow()
        session.commit()
        self.refresh_users()

class DispensaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(AddUserScreen(name='add_user'))
        sm.add_widget(UserListScreen(name='user_list'))
        return sm

    def add_user(self, user_name):
        if user_name.strip():
            new_user = User(name=user_name)
            session.add(new_user)
            session.commit()
            self.root.get_screen('user_list').refresh_users()

    def copy_to_clipboard(self):
        users = session.query(User).filter_by(afastado=False).all()
        date_str = datetime.now().strftime('%d/%m/%Y')
        text = f'*DISPENSA ATUALIZADA* {date_str}\n\n'
        for idx, user in enumerate(users, start=1):
            text += f'*{idx}* - _{user.name}_\n'
        Clipboard.copy(text)
        print('Texto copiado para a área de transferência')

if __name__ == '__main__':
    DispensaApp().run()
