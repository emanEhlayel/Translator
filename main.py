import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from deep_translator import GoogleTranslator
import threading
from datetime import datetime


class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("أداة الترجمة المتقدمة")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fa")

        # إعداد الخطوط والألوان
        self.title_font = ("Arial", 16, "bold")
        self.label_font = ("Arial", 11)
        self.button_font = ("Arial", 11, "bold")
        self.text_font = ("Arial", 12)

        # اللغات المتاحة
        self.languages = GoogleTranslator().get_supported_languages(as_dict=True)
        self.language_names = list(self.languages.keys())
        self.language_codes = list(self.languages.values())

        # إنشاء واجهة المستخدم
        self.create_widgets()

        # تعيين اللغة الافتراضية
        self.from_lang_combo.current(self.language_names.index('english'))
        self.to_lang_combo.current(self.language_names.index('arabic'))

    def create_widgets(self):
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg="#4a6fa5")
        title_frame.pack(fill="x", pady=(0, 15))

        # العنوان
        title_label = tk.Label(
            title_frame,
            text="أداة الترجمة المتعددة اللغات",
            font=self.title_font,
            fg="white",
            bg="#4a6fa5",
            pady=10
        )
        title_label.pack()

        # إطار إدخال النص
        input_frame = tk.Frame(self.root, bg="#f5f7fa")
        input_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            input_frame,
            text="النص الأصلي:",
            font=self.label_font,
            bg="#f5f7fa"
        ).pack(anchor="w", pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            width=60,
            height=8,
            font=self.text_font,
            bg="white",
            fg="#333",
            insertbackground="#4a6fa5",
            selectbackground="#c2d4f0"
        )
        self.input_text.pack()

        # إطار اختيار اللغات
        lang_frame = tk.Frame(self.root, bg="#f5f7fa")
        lang_frame.pack(fill="x", padx=20, pady=10)

        # من لغة
        from_lang_frame = tk.Frame(lang_frame, bg="#f5f7fa")
        from_lang_frame.pack(side="left", expand=True)

        tk.Label(
            from_lang_frame,
            text="من لغة:",
            font=self.label_font,
            bg="#f5f7fa"
        ).pack(anchor="w")

        self.from_lang_combo = ttk.Combobox(
            from_lang_frame,
            values=self.language_names,
            font=self.label_font,
            state="readonly"
        )
        self.from_lang_combo.pack(fill="x", pady=5)

        # إلى لغة
        to_lang_frame = tk.Frame(lang_frame, bg="#f5f7fa")
        to_lang_frame.pack(side="right", expand=True)

        tk.Label(
            to_lang_frame,
            text="إلى لغة:",
            font=self.label_font,
            bg="#f5f7fa"
        ).pack(anchor="w")

        self.to_lang_combo = ttk.Combobox(
            to_lang_frame,
            values=self.language_names,
            font=self.label_font,
            state="readonly"
        )
        self.to_lang_combo.pack(fill="x", pady=5)

        # زر الترجمة
        translate_btn = tk.Button(
            self.root,
            text="ترجمة",
            font=self.button_font,
            bg="#4a6fa5",
            fg="white",
            activebackground="#3a5a80",
            activeforeground="white",
            relief="flat",
            padx=20,
            command=self.start_translation_thread
        )
        translate_btn.pack(pady=10)

        # إطار النتيجة
        result_frame = tk.Frame(self.root, bg="#f5f7fa")
        result_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            result_frame,
            text="النص المترجم:",
            font=self.label_font,
            bg="#f5f7fa"
        ).pack(anchor="w", pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            width=60,
            height=8,
            font=self.text_font,
            bg="white",
            fg="#333",
            state="normal",
            insertbackground="#4a6fa5",
            selectbackground="#c2d4f0"
        )
        self.output_text.pack()

        # إطار الحالة
        status_frame = tk.Frame(self.root, bg="#f5f7fa")
        status_frame.pack(fill="x", padx=20, pady=(5, 10))

        self.status_label = tk.Label(
            status_frame,
            text="جاهز للترجمة",
            font=("Arial", 9),
            bg="#f5f7fa",
            fg="#666"
        )
        self.status_label.pack(side="left")

        self.time_label = tk.Label(
            status_frame,
            text="",
            font=("Arial", 9),
            bg="#f5f7fa",
            fg="#666"
        )
        self.time_label.pack(side="right")

        # نسخ النص المترجم
        copy_btn = tk.Button(
            self.root,
            text="نسخ النص المترجم",
            font=("Arial", 10),
            bg="#e0e5ec",
            fg="#333",
            activebackground="#d0d5dc",
            relief="flat",
            command=self.copy_translated_text
        )
        copy_btn.pack(pady=(0, 10))

    def start_translation_thread(self):
        # تشغيل الترجمة في thread منفصل لتجنب تجميد الواجهة
        thread = threading.Thread(target=self.translate_text)
        thread.start()

    def translate_text(self):
        try:
            self.update_status("جاري الترجمة...", "#4a6fa5")

            # الحصول على النص المدخل
            text_to_translate = self.input_text.get("1.0", tk.END).strip()

            if not text_to_translate:
                messagebox.showwarning("تحذير", "الرجاء إدخال نص للترجمة")
                self.update_status("جاهز للترجمة", "#666")
                return

            # الحصول على اللغات المحددة
            from_lang = self.languages[self.from_lang_combo.get()]
            to_lang = self.languages[self.to_lang_combo.get()]

            # تنفيذ الترجمة
            translated = GoogleTranslator(source=from_lang, target=to_lang).translate(text_to_translate)

            # عرض النتيجة
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
            self.output_text.config(state="disabled")

            # تحديث الحالة
            now = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=f"آخر ترجمة: {now}")
            self.update_status("تمت الترجمة بنجاح", "#2e7d32")

        except Exception as e:
            self.update_status("فشل في الترجمة", "#c62828")
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الترجمة: {str(e)}")

    def copy_translated_text(self):
        try:
            translated_text = self.output_text.get("1.0", tk.END).strip()
            if translated_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(translated_text)
                self.update_status("تم نسخ النص المترجم", "#2e7d32")
            else:
                messagebox.showwarning("تحذير", "لا يوجد نص مترجم للنسخ")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في نسخ النص: {str(e)}")

    def update_status(self, message, color):
        self.status_label.config(text=message, fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)

    # إضافة أيقونة للتطبيق (اختياري)
    try:
        root.iconbitmap("translate.ico")  # يمكنك وضع أيقونة في نفس المجلد
    except:
        pass

    root.mainloop()
