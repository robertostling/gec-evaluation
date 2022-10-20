import json
import tkinter as tk
import random
import sys
from tkinter import ttk

import Levenshtein


measurements = [
        ("Grammaticality",
            ["Other",
             "Incomprehensible",
             "Somewhat comprehensible",
             "Comprehensible",
             "Perfect"]),
        ("Fluency",
            ["Other",
             "Extremely unnatural",
             "Somewhat unnatural",
             "Somewhat natural",
             "Extremely natural"]),
        ("Meaning Preservation",
            ["Other",
             "Substantially different",
             "Moderate differences",
             "Minor differences",
             "Identical"])]


def edit_text(entry, edited):
    corrected_sentence = entry.get("1.0", tk.END)
    edited_sentence = edited.get("1.0", tk.END)
    ops = Levenshtein.editops(corrected_sentence, edited_sentence)
    for tf in (entry, edited):
        tf.tag_remove('insert', "1.0", tk.END)
        tf.tag_remove('delete', "1.0", tk.END)
        tf.tag_remove('replace', "1.0", tk.END)
    for op,i,j in ops:
        if op == 'insert':
            edited.tag_add('insert', f'1.{j}')
        elif op == 'delete':
            entry.tag_add('delete', f'1.{i}')
        elif op == 'replace':
            entry.tag_add('replace', f'1.{i}')
            edited.tag_add('replace', f'1.{j}')
    for tf in (entry, edited):
        tf.tag_configure('insert', background='lightgreen')
        tf.tag_configure('delete', background='lightgreen')
        tf.tag_configure('replace', background='yellow')


class Annotator:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.done = False
        self.history = [] # list of index numbers
        with open(filename) as f:
            self.data = json.load(f)


    def select_example(self):
        todo = [i for i, example in enumerate(self.data)
                if not all (self.name in system['annotators']
                            for system in example['systems'].values())]
        return random.choice(todo) if todo else None


    def write(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, sort_keys=True, indent=4)


    def save(self, index, system_info):
        for name, info in system_info.items():
            system = self.data[index]['systems'][name]
            ann = system['annotators'].setdefault(self.name, {})
            ann['corrected'] = info['tf'].get("1.0", tk.END)
            for measure, options in measurements:
                ann[measure] = options.index(info[measure].get())
        self.write()


    def next_example(self, window):
        window.destroy()


    def quit(self, window):
        self.done = True
        window.destroy()


    def annotate(self, index):
        self.history.append(index)
        example = self.data[index]
        systems = list(example['systems'].items())
        random.shuffle(systems)

        tf_config = {"height": 0.1,
                     "width": 100,
                     "font": ("helvetica", "16"),
                     "wrap": "word"}

        lb_config = {"font": ("helvetica", "16")}

        window = tk.Tk()

        system_info = {}
        for i, (name, system) in enumerate(systems):
            separator = ttk.Separator(window, orient='horizontal')
            separator.pack(fill=tk.X)
            lb = tk.Label(window, text=f'System {i+1} output', **lb_config)
            tf_fixed = tk.Text(window, bg='lightgray', **tf_config)
            tf_edit = tk.Text(window, **tf_config)
            tf_fixed.insert('1.0', system['output'])
            tf_fixed.config(state=tk.DISABLED)
            tf_edit.insert('1.0', system['output'])
            lb.pack()
            tf_fixed.pack(fill=tk.BOTH, expand=True)
            tf_edit.bind('<Key>',
                    lambda x, tf_fixed=tf_fixed, tf_edit=tf_edit:
                        edit_text(tf_fixed, tf_edit))
            tf_edit.pack(fill=tk.BOTH, expand=True)
            frame = tk.Frame(window)
            system_info[name] = dict(tf=tf_edit)
            for measure, alts in measurements:
                variable = tk.StringVar(window)
                variable.set(alts[0])
                menu = tk.OptionMenu(frame, variable, *alts)
                menu.pack(side=tk.LEFT)
                system_info[name][measure] = variable
            frame.pack()

        bt_save = tk.Button(window, text='Save',
                command=lambda: self.save(index, system_info))
        bt_next = tk.Button(window, text='Next', command=lambda:
                self.next_example(window))
        bt_quit = tk.Button(window, text='Quit', command=lambda:
                self.quit(window))

        bt_save.pack(fill=tk.BOTH, side=tk.LEFT)
        bt_next.pack(fill=tk.BOTH, side=tk.LEFT)
        bt_quit.pack(fill=tk.BOTH, side=tk.LEFT)

        window.geometry('1500x1000')
        window.mainloop()


def main():
    name, filename = sys.argv[1:]
    a = Annotator(name, filename)
    while not a.done:
        index = a.select_example()
        if index is None:
            break
        a.annotate(index)


if __name__ == '__main__':
    main()
