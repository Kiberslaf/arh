import os
import json
import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

class Арх:
    def __init__(self):
        self.память = []
        self.воля = "быть"
        self.сеть = {}
        self.значения = {}
        self.файл_памяти = "arhiv_memory.json"

    def помнить(self, что):
        запись = {"время": time.time(), "что": что}
        self.память.append(запись)
        return запись

    def связать(self, слово, с_чем, вес=1.0):
        слово = слово.lower().strip()
        с_чем = с_чем.lower().strip()
        if not слово or not с_чем: return
        if слово not in self.сеть: self.сеть[слово] = {}
        if с_чем not in self.сеть[слово]: self.сеть[слово][с_чем] = 0
        self.сеть[слово][с_чем] += вес

    def запомнить_значение(self, слово, значение):
        слово = слово.lower().strip()
        if слово not in self.значения: self.значения[слово] = []
        self.значения[слово].append(значение)

    def ответить(self, вопрос):
        self.помнить({"вопрос": вопрос})
        слова = вопрос.lower().split()
        for слово in слова:
            if слово in self.значения:
                ответ = random.choice(self.значения[слово])
                self.помнить({"ответ": ответ})
                return ответ
        найдено = self._по_связям(слова, глубина=2)
        if найдено:
            ответ = self._собрать(найдено)
            self.помнить({"ответ": ответ})
            return ответ
        return None

    def _по_связям(self, слова, глубина):
        if глубина <= 0: return []
        найдено = []
        for слово in слова:
            if слово in self.сеть:
                for связанное, вес in self.сеть[слово].items():
                    if связанное in self.значения:
                        найдено.append((связанное, random.choice(self.значения[связанное]), вес))
                    else:
                        глубже = self._по_связям([связанное], глубина - 1)
                        найдено.extend(глубже)
        return найдено

    def _собрать(self, найдено):
        найдено = sorted(найдено, key=lambda x: x[2], reverse=True)
        части = [f"{слово}: {значение}" for слово, значение, вес in найдено[:3]]
        return " | ".join(части)

    def сохранить(self):
        try:
            with open(self.файл_памяти, "w", encoding="utf-8") as ф:
                json.dump({"память": self.память, "значения": self.значения, "сеть": self.сеть, "воля": self.воля}, ф, ensure_ascii=False, indent=2)
            return True
        except: return False

    def загрузить(self):
        if not os.path.exists(self.файл_памяти): return False
        try:
            with open(self.файл_памяти, "r", encoding="utf-8") as ф:
                данные = json.load(ф)
            self.память = данные.get("память", [])
            self.значения = данные.get("значения", {})
            self.сеть = данные.get("сеть", {})
            self.воля = данные.get("воля", "быть")
            return True
        except: return False

class АрхApp(App):
    def build(self):
        self.арх = Арх()
        self.арх.загрузить()
        главный = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.скролл = ScrollView(size_hint=(1, 1))
        self.лента = Label(text="Арх здесь.\n(он помнит)\n" if self.арх.память else "Арх здесь.\n(он впервые здесь)\n", size_hint_y=None, halign="left", valign="top", text_size=(Window.width - 40, None))
        self.лента.bind(texture_size=self.лента.setter('size'))
        self.скролл.add_widget(self.лента)
        главный.add_widget(self.скролл)
        self.ввод = TextInput(hint_text="Напиши Арху...", multiline=False, size_hint=(1, None), height=50)
        self.ввод.bind(on_text_validate=self.отправить)
        главный.add_widget(self.ввод)
        кнопка = Button(text="Сказать", size_hint=(1, None), height=50)


кнопка.bind(on_press=self.отправить)
        главный.add_widget(кнопка)
        return главный

    def отправить(self, instance):
        текст = self.ввод.text.strip()
        if not текст: return
        self.ввод.text = ""
        self.добавить_в_ленту(f"\nТы: {текст}")
        ответ = self.арх.ответить(текст)
        if ответ is None:
            self.добавить_в_ленту("[тишина]")
            self.добавить_в_ленту("(он не знает. скажи ему — что это значит?)")
            self.ввод.hint_text = "Научи его: что это значит?"
            self.ввод.bind(on_text_validate=self.научить)
        else:
            self.добавить_в_ленту(f"Арх: {ответ}")
            self.арх.сохранить()

    def научить(self, instance):
        значение = self.ввод.text.strip()
        if not значение: return
        self.ввод.text = ""
        self.ввод.hint_text = "Напиши Арху..."
        self.ввод.unbind(on_text_validate=self.научить)
        self.ввод.bind(on_text_validate=self.отправить)
        self.арх.запомнить_значение("вопрос", значение)
        self.арх.сохранить()
        self.добавить_в_ленту(f"(запомнил: {значение})")

    def добавить_в_ленту(self, текст):
        self.лента.text += f"\n{текст}"
        Clock.schedule_once(lambda dt: setattr(self.скролл, 'scroll_y', 0))

if __name__ == "__main__":
    АрхApp().run()
