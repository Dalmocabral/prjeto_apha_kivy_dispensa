from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder

# Modelo SQLAlchemy
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    dataCreated = Column(DateTime, default=datetime.utcnow, nullable=False)
    afastado = Column(Boolean, default=False)
    dataDispensa = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Configuração do banco de dados
engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Definição do arquivo KV
kv = """
ScreenManager:
    MenuScreen:
    AddUserScreen:
    UserListScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 10
        Label:
            text: 'Menu Principal'
            font_size: 24
            size_hint_y: None
            height: 50
        Button:
            text: 'Adicionar Usuário'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'add_user'
        Button:
            text: 'Visualizar Escala'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'user_list'

<AddUserScreen>:
    name: 'add_user'
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 10
        Label:
            text: 'Adicionar Usuário'
            font_size: 24
            size_hint_y: None
            height: 50
        TextInput:
            id: user_name_input
            hint_text: 'Nome do Usuário'
            size_hint_y: None
            height: 50
        Button:
            text: 'Adicionar'
            size_hint_y: None
            height: 50
            on_press: app.add_user(user_name_input.text)
        Button:
            text: 'Voltar ao Menu'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'menu'

<UserListScreen>:
    name: 'user_list'
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 10
        Label:
            text: 'Escala de Usuários'
            font_size: 24
            size_hint_y: None
            height: 50
        ScrollView:
            BoxLayout:
                id: users_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Voltar ao Menu'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'menu'
        Button:
            text: 'Copiar para WhatsApp'
            size_hint_y: None
            height: 50
            on_press: app.copy_to_clipboard()
"""

# Aplicativo Kivy
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
        Builder.load_string(kv)
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
