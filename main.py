from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from deep_translator import GoogleTranslator
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
import threading

Builder.load_string('''
<TranslationApp>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    canvas.before:
        Color:
            rgba: get_color_from_hex('#f5f7fa')
        Rectangle:
            pos: self.pos
            size: self.size

<HeaderLabel@Label>:
    size_hint_y: None
    height: 50
    font_size: 20
    bold: True
    color: get_color_from_hex('#ffffff')
    canvas.before:
        Color:
            rgba: get_color_from_hex('#4a6fa5')
        Rectangle:
            pos: self.pos
            size: self.size

<ScrollableLabel>:
    text: ''
    size_hint_y: None
    height: max(self.texture_size[1], 200)
    padding: [10, 10]
    halign: 'right'
    valign: 'top'
    markup: True
    canvas.before:
        Color:
            rgba: get_color_from_hex('#ffffff')
        Rectangle:
            pos: self.pos
            size: self.size
''')

class ScrollableLabel(Label):
    pass

class TranslationApp(BoxLayout):
    def __init__(self, **kwargs):
        super(TranslationApp, self).__init__(**kwargs)
        
        # اللغات المتاحة
        self.languages = GoogleTranslator().get_supported_languages(as_dict=True)
        self.language_names = list(self.languages.keys())
        self.language_codes = list(self.languages.values())
        
        # واجهة المستخدم
        self.build_ui()
    
    def build_ui(self):
        # العنوان
        self.header = Label(
            text='أداة الترجمة المتعددة اللغات',
            size_hint=(1, None),
            height=60,
            font_size=24,
            bold=True,
            color=get_color_from_hex('#ffffff'),
        )
        self.header.canvas.before.clear()
        with self.header.canvas.before:
            get_color_from_hex('#4a6fa5')
        
        self.add_widget(self.header)
        
        # إدخال النص
        self.add_widget(Label(text='النص الأصلي:', size_hint=(1, None), height=30, halign='right'))
        
        self.input_text = TextInput(
            multiline=True,
            size_hint=(1, None),
            height=150,
            font_size=16,
            background_color=get_color_from_hex('#ffffff'),
            foreground_color=get_color_from_hex('#333333'),
            padding=[10, 10],
            halign='right'
        )
        self.add_widget(self.input_text)
        
        # اختيار اللغات
        lang_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=10)
        
        from_lang_layout = BoxLayout(orientation='vertical', spacing=5)
        from_lang_layout.add_widget(Label(text='من لغة:', size_hint=(1, None), height=30, halign='right'))
        self.from_lang = Spinner(
            text='english',
            values=self.language_names,
            size_hint=(1, None),
            height=40,
            font_size=16
        )
        from_lang_layout.add_widget(self.from_lang)
        lang_layout.add_widget(from_lang_layout)
        
        to_lang_layout = BoxLayout(orientation='vertical', spacing=5)
        to_lang_layout.add_widget(Label(text='إلى لغة:', size_hint=(1, None), height=30, halign='right'))
        self.to_lang = Spinner(
            text='arabic',
            values=self.language_names,
            size_hint=(1, None),
            height=40,
            font_size=16
        )
        to_lang_layout.add_widget(self.to_lang)
        lang_layout.add_widget(to_lang_layout)
        
        self.add_widget(lang_layout)
        
        # زر الترجمة
        self.translate_btn = Button(
            text='ترجمة',
            size_hint=(1, None),
            height=50,
            font_size=18,
            background_color=get_color_from_hex('#4a6fa5'),
            color=get_color_from_hex('#ffffff'),
            on_press=self.start_translation_thread
        )
        self.add_widget(self.translate_btn)
        
        # النتيجة
        self.add_widget(Label(text='النص المترجم:', size_hint=(1, None), height=30, halign='right'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        self.output_text = ScrollableLabel(
            font_size=16,
            color=get_color_from_hex('#333333')
        )
        scroll_view.add_widget(self.output_text)
        self.add_widget(scroll_view)
        
        # نسخ النص
        self.copy_btn = Button(
            text='نسخ النص المترجم',
            size_hint=(1, None),
            height=45,
            font_size=16,
            background_color=get_color_from_hex('#e0e5ec'),
            color=get_color_from_hex('#333333'),
            on_press=self.copy_translated_text
        )
        self.add_widget(self.copy_btn)
        
        # الحالة
        self.status_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        self.status_label = Label(text='جاهز للترجمة', color=get_color_from_hex('#666666'))
        self.time_label = Label(text='', color=get_color_from_hex('#666666'))
        self.status_bar.add_widget(self.status_label)
        self.status_bar.add_widget(self.time_label)
        self.add_widget(self.status_bar)
    
    def start_translation_thread(self, instance):
        threading.Thread(target=self.translate_text).start()
    
    def translate_text(self):
        Clock.schedule_once(lambda dt: self.update_status("جاري الترجمة...", '#4a6fa5'))
        
        try:
            text = self.input_text.text.strip()
            if not text:
                Clock.schedule_once(lambda dt: self.show_message("تحذير", "الرجاء إدخال نص للترجمة"))
                Clock.schedule_once(lambda dt: self.update_status("جاهز للترجمة", '#666666'))
                return
            
            from_lang = self.languages[self.from_lang.text]
            to_lang = self.languages[self.to_lang.text]
            
            translated = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
            
            Clock.schedule_once(lambda dt: setattr(self.output_text, 'text', translated))
            Clock.schedule_once(lambda dt: self.update_status("تمت الترجمة بنجاح", '#2e7d32'))
        
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status("فشل في الترجمة", '#c62828'))
            Clock.schedule_once(lambda dt: self.show_message("خطأ", f"حدث خطأ: {str(e)}"))
    
    def copy_translated_text(self, instance):
        if self.output_text.text.strip():
            Clipboard.copy(self.output_text.text)
            self.update_status("تم نسخ النص المترجم", '#2e7d32')
        else:
            self.show_message("تحذير", "لا يوجد نص مترجم للنسخ")
    
    def update_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = get_color_from_hex(color)
    
    def show_message(self, title, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        content = Label(text=message, padding=10)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        content.bind(size=lambda s, w: s.setter('text_size')(s, w))
        popup.open()


class MobileTranslatorApp(App):
    def build(self):
        self.title = 'أداة الترجمة'
        return TranslationApp()


if __name__ == '__main__':
    MobileTranslatorApp().run()
