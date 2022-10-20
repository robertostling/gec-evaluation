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


tf_config = {"height": 0.1,
             "width": 100,
             "font": ("helvetica", "12"),
             "wrap": "word"}


lb_config = {"font": ("helvetica", "12")}


def edit_text(entry, edited):
    corrected_sentence = entry.get("1.0", tk.END).strip()
    edited_sentence = edited.get("1.0", tk.END).strip()
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
        self.annotator_name = name
        self.filename = filename
        self.done = False
        self.history = [] # list of index numbers
        with open(filename) as f:
            self.metadata = json.load(f)
            # Short cut to the data table (list of items)
            self.data = self.metadata['data']


    def get_item_index(self):
        next_item = self.metadata['next_item']
        item_order = self.metadata['item_order']
        return item_order[next_item]


    def write(self):
        with open(self.filename, 'w') as f:
            json.dump(self.metadata, f, sort_keys=True, indent=4)


    def save(self, index, system_info, tf_ref, bt_save):
        tf_ref.config(state=tk.NORMAL)
        tf_ref.delete("1.0", tk.END)
        if self.confirmed:
            for name, info in system_info.items():
                system = self.data[index]['systems'][name]
                ann = system['annotators'].setdefault(self.annotator_name, {})
                ann['corrected'] = info['tf'].get("1.0", tk.END).strip()
                for measure, options in measurements:
                    value = info[measure].get()
                    if value in options:
                        ann[measure] = options.index(value)
            self.write()
            self.confirmed = False
        else:
            tf_ref.insert("1.0", self.data[index]['reference'])
            self.confirmed = True
        bt_save['text'] = 'Confirm' if self.confirmed else 'Save'
        tf_ref.config(state=tk.DISABLED)


    def change_example(self, window, change):
        next_item = self.metadata['next_item']
        item_order = self.metadata['item_order']
        self.metadata['next_item'] = (next_item + change) % len(item_order)
        self.write()
        window.destroy()


    def quit(self, window):
        self.done = True
        window.destroy()


    def annotate(self):
        index = self.get_item_index()
        self.history.append(index)
        example = self.data[index]
        systems = list(example['systems'].items())
        random.shuffle(systems)

        window = tk.Tk()

        system_info = {}
        for i, (name, system) in enumerate(systems):
            existing = system['annotators'].get(self.annotator_name, {})
            separator = ttk.Separator(window, orient='horizontal')
            separator.pack(fill=tk.X)
            lb = tk.Label(window, text=f'System {i+1} output', **lb_config)
            lb.pack()
            tf_fixed = tk.Text(window, bg='lightgray', **tf_config)
            tf_edit = tk.Text(window, **tf_config)
            tf_fixed.insert('1.0', system['output'])
            tf_fixed.config(state=tk.DISABLED)
            tf_edit.insert('1.0', existing.get('corrected', system['output']))
            tf_fixed.pack(fill=tk.BOTH, expand=True)
            tf_edit.bind('<Key>',
                    lambda x, tf_fixed=tf_fixed, tf_edit=tf_edit:
                        edit_text(tf_fixed, tf_edit))
            tf_edit.pack(fill=tk.BOTH, expand=True)
            edit_text(tf_fixed, tf_edit)
            frame = tk.Frame(window)
            system_info[name] = dict(tf=tf_edit)
            for measure, alts in measurements:
                variable = tk.StringVar(window)
                value = existing.get(measure)
                if value is None:
                    variable.set(f'--- {measure} rating ---')
                else:
                    variable.set(alts[value])
                menu = tk.OptionMenu(frame, variable, *alts)
                menu.pack(side=tk.LEFT)
                system_info[name][measure] = variable
            frame.pack()

        separator = ttk.Separator(window, orient='horizontal')
        separator.pack(fill=tk.X)
        lb = tk.Label(window, text=f'Intended meaning', **lb_config)
        lb.pack()
        tf_ref = tk.Text(window, bg='black', fg='white', **tf_config)
        tf_ref.config(state=tk.DISABLED)
        tf_ref.pack(fill=tk.BOTH, expand=True)

        self.confirmed = False

        bt_save = tk.Button(window, text='Save',
                command=lambda: self.save(index, system_info, tf_ref, bt_save))
        bt_prev = tk.Button(window, text='<<<', command=lambda:
                self.change_example(window, -1))
        bt_next = tk.Button(window, text='>>>', command=lambda:
                self.change_example(window, 1))
        bt_quit = tk.Button(window, text='Quit', command=lambda:
                self.quit(window))

        bt_save.pack(fill=tk.BOTH, side=tk.LEFT)
        bt_prev.pack(fill=tk.BOTH, side=tk.LEFT)
        bt_next.pack(fill=tk.BOTH, side=tk.LEFT)
        bt_quit.pack(fill=tk.BOTH, side=tk.LEFT)

        window.geometry('1500x1000')
        window.mainloop()


def main():
    name, filename = sys.argv[1:]
    a = Annotator(name, filename)
    while not a.done:
        a.annotate()


if __name__ == '__main__':
    main()
