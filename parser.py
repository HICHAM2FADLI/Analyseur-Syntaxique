import tkinter as tk
from tkinter import filedialog
import arabic_reshaper
from bidi.algorithm import get_display

class ArabicParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = 0

    def parse(self):
        self.current_token = self.tokens[self.index]
        self.programme()

    def match(self, expected_token):
        if self.current_token == expected_token:
            self.consume_token()
        else:
            raise SyntaxError(f"متوقع {expected_token}، ولكن تم العثور على {self.current_token}")

    def consume_token(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def programme(self):
        while self.current_token:
            self.instruction()

    def instruction(self):
        if self.current_token == "اقرأ":
            self.lecture()
        elif self.current_token == "اكتب":
            self.ecriture()
        elif self.current_token == "إذا":
            self.condition()
        elif self.current_token == "بينما":
            self.boucle()
        elif self.current_token == "معقوفة":
            self.bloc()
        else:
            self.affectation()

    def lecture(self):
        self.match("اقرأ")
        self.match("قوس")
        self.match("المعرف")
        self.match("قوس")
        self.match("نهاية_التعليمات")

    def ecriture(self):
        self.match("اكتب")
        self.match("قوس")

        while self.current_token in ["النص", "المعرف"]:
            if self.current_token == "النص":
                self.match("النص")
            elif self.current_token == "المعرف":
                self.match("المعرف")

            # Vérifier si un autre token est attendu
            if self.current_token == "الجمع":
                self.match("الجمع")
            else:
                break

        self.match("قوس")
        self.match("نهاية_التعليمات")


    def affectation(self):
        self.match("المعرف")
        self.match("تساوي")
        self.expression()
        self.match("نهاية_التعليمات")

    def condition(self):
        self.match("إذا")
        self.expression()
        self.match("ثم")
        self.bloc()
        if self.current_token == "إلا":
            self.match("إلا")
            self.bloc()
        self.match("انتهى")

    def boucle(self):
        self.match("بينما")
        self.expression()
        self.match("فعل")
        self.bloc()
        self.match("انتهى")

    def bloc(self):
        self.match("معقوفة")
        while self.current_token != "معقوفة":
            self.instruction()
        self.match("معقوفة")

    def expression(self):
        self.terme()
        while self.current_token in ["زائد", "ناقص","أكبر_من","أصغر_من"]:
            self.match(self.current_token)
            self.terme()

    def terme(self):
        self.facteur()
        while self.current_token in ["ضرب", "قسمة","زائد", "ناقص"]:
            self.match(self.current_token)
            self.facteur()

    def facteur(self):
        if self.current_token == "المعرف" or self.current_token == "العدد":
            self.match(self.current_token)
        elif self.current_token == "قوس":
            self.match("قوس")
            self.expression()
            self.match("قوس")
        elif self.current_token == "ليس":
            self.match("ليس")
            self.facteur()
        else:
            raise SyntaxError(f"رمز غير متوقع: {self.current_token}")

class TokenAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("محلل الرموز")

        self.label = tk.Label(root, text="قائمة الرموز (مفصولة بمسافات) :")
        self.label.pack()

        self.tokens_entry = tk.Text(root, height=5, width=80)
        self.tokens_entry.pack()

        self.load_button = tk.Button(root, text="تحميل ملف", command=self.load_file)
        self.load_button.pack()

        self.analyze_button = tk.Button(root, text="تحليل", command=self.analyze_tokens)
        self.analyze_button.pack()

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        self.tokens_entry.tag_configure('المعرف', foreground='blue')
        self.tokens_entry.tag_configure('العدد', foreground='green')
        self.tokens_entry.tag_configure('مفتاح', foreground='red')
        self.tokens_entry.tag_configure('علامة', foreground='purple')
        self.tokens_entry.tag_configure('مشغل', foreground='orange')

    def load_file(self):
        file_path = filedialog.askopenfilename(title="اختيار ملف", filetypes=[("ملفات النصوص", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.tokens_entry.delete("1.0", tk.END)
                self.tokens_entry.insert(tk.END, content)
                self.tokens_entry.tag_configure('rtl', justify='right')
                self.tokens_entry.tag_add('rtl', '1.0', 'end')

    def analyze_tokens(self):
        tokens = self.tokens_entry.get("1.0", tk.END).split()
        result = analyze_tokens(tokens)
        self.result_label.config(text=result)
        for token in tokens:
            if token.isalpha():
                self.tokens_entry.tag_add('المعرف', tk.END+'-'+f'-{len(token)}c', tk.END)
            elif token.isdigit():
                self.tokens_entry.tag_add('العدد', tk.END+'-'+f'-{len(token)}c', tk.END)
            elif token in ["اقرأ", "اكتب", "تساوي", "ثم", "إلا", "انتهى", "بينما", "فعل"]:
                self.tokens_entry.tag_add('مشغل', tk.END+'-'+f'-{len(token)}c', tk.END)
            elif token in ["إذا"]:
                self.tokens_entry.tag_add('مفتاح', tk.END+'-'+f'-{len(token)}c', tk.END)
            elif token in ["معقوفة", "نهاية_التعليمات"]:
                self.tokens_entry.tag_add('علامة', tk.END+'-'+f'-{len(token)}c', tk.END)
        self.colorize_tokens(tokens)
        
    def colorize_tokens(self, tokens):
        text = self.tokens_entry.get("1.0", tk.END)
        self.tokens_entry.delete("1.0", tk.END)

        for token in tokens:
            if token == "المعرف":
                self.tokens_entry.insert(tk.END, token, "المعرف")
            elif token == "العدد":
                self.tokens_entry.insert(tk.END, token, "العدد")
            elif token in ["اقرأ", "اكتب", "تساوي", "ثم", "إلا", "انتهى", "بينما", "فعل"]:
                self.tokens_entry.insert(tk.END, token, "مشغل")
            elif token in ["إذا"]:
                self.tokens_entry.insert(tk.END, token, "مفتاح")
            elif token in ["معقوفة", "نهاية_التعليمات"]:
                self.tokens_entry.insert(tk.END, token, "علامة")
            else:
                self.tokens_entry.insert(tk.END, token)

            self.tokens_entry.insert(tk.END, " ")

        self.tokens_entry.tag_configure("المعرف", foreground="blue")
        self.tokens_entry.tag_configure("العدد", foreground="green")
        self.tokens_entry.tag_configure('مفتاح', foreground='red')
        self.tokens_entry.tag_configure('علامة', foreground='purple')
        self.tokens_entry.tag_configure('مشغل', foreground='orange')
        self.tokens_entry.tag_configure('rtl', justify='right')
        self.tokens_entry.tag_add('rtl', '1.0', 'end')

def analyze_tokens(tokens):
    try:
        parser = ArabicParser(tokens)
        parser.parse()
        return "تحليل ناجح."
    except Exception as e:
        return f"فشل التحليل بسبب: {str(e)}"

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenAnalyzerApp(root)
    root.mainloop()
