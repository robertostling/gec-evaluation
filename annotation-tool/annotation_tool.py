import os
import random
import tkinter as tk
import json
from collections import defaultdict
import sys
import Levenshtein
import glob

if len(sys.argv) <3:
    print("Please provide an annotator name and the target folder where your annotations will be saved.")
    print("The folder will be created automatically if it does not exist.")
    print("e.g. python annotation_tool.py murathan /home/murathan/Desktop/gec")

    quit()
annotator_name = sys.argv[1]
output_folder = sys.argv[2]
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file_name =f"{output_folder}/{annotator_name}.json"


def read_file_lines(filename):
    with open(filename) as f:
        return [line.strip() for line in f]


random.seed(3)
### files ###
accepted_extensions = sorted(
        [".s2", ".granska", ".mt-base", ".mt-large", ".mystery"])
show_it = True
sentence_count = 0
filename = ""
counter_text = "Sentence %i/%i"
tf_config = {"height": 0.1, "width": 100, "font": ("helvetica", "18"), "wrap": "word"}
model_output_pattern = "data/playing/Nyberg.CEFR_ABC.dev.orig.round1.*"
human_corrected_file = "data/playing/Nyberg.CEFR_ABC.dev.corr.round1"
human_corrected = read_file_lines(human_corrected_file)
limit = len(human_corrected)
seen_extensions = []
model_outputs = []
for filename in sorted(glob.glob(model_output_pattern)):
    extension = os.path.splitext(os.path.basename(filename))[1]
    if extension not in accepted_extensions:
        print(f'WARNING: unexpected extension ({extension}), skipping')
        continue
    seen_extensions.append(extension)
    model_outputs.extend(read_file_lines(filename))

randomized_order = list(range(limit*len(seen_extensions)))
random.shuffle(randomized_order)


if os.path.exists(output_file_name):
    annotations = json.load(open(output_file_name))
    sentence_count = len(annotations) + 1
else:
    annotations = []


###

def get_random_index():
    global sentence_count
    #print(sentence_count,  randomized_order[sentence_count])
    #print(seen_extensions[int(randomized_order[sentence_count]/limit)],  randomized_order[sentence_count]% limit)

    return randomized_order[sentence_count]


# Functions
def hide_widget(widget):
    global show_it, sentence_count
    randomized_index = get_random_index()
    randomized_index = randomized_index % limit
    widget.config(state=tk.NORMAL)
    if show_it:
        widget.insert(0.0, human_corrected[randomized_index])
        show_it = False
    else:
        widget.delete(0.0, "end")
        show_it = True
    widget.config(state=tk.DISABLED)


def reset_tf(widget, text,disable=False):
    if disable:
        widget.config(state=tk.NORMAL)
    widget.delete(0.0, "end")
    widget.insert(0.0, text)
    if disable:
        widget.config(state=tk.DISABLED)


def reset(sentence_count):
    reset_tf(tf_human, "", disable=True)
    randomized_index = get_random_index()

    reset_tf(tf_model, model_outputs[randomized_index ], disable=True)
    if len(annotations) > sentence_count:
        tf_entry_initial = annotations[sentence_count]["corrected_prediction"]
    else:
        tf_entry_initial = model_outputs[randomized_index ]
    reset_tf(tf_entry, tf_entry_initial, disable=False)
    global show_it
    show_it = True


def save():
    output_file = open(output_file_name, 'w', encoding='utf-8')
    x = json.dumps(annotations, indent=2)
    output_file.write(x)


def edit_text(entry, edited):
    corrected_sentence = entry.get("1.0", tk.END)
    edited_sentence = edited.get("1.0", tk.END)
    ops = Levenshtein.editops(corrected_sentence, edited_sentence)
    src_mod = sorted({i for _,i,_ in ops})
    trg_mod = sorted({j for _,_,j in ops})
    entry.tag_remove("modified", "1.0", tk.END)
    edited.tag_remove("modified", "1.0", tk.END)
    for i in src_mod:
        entry.tag_add('modified', f'1.{i}')
    for i in trg_mod:
        edited.tag_add('modified', f'1.{i}')
    #print('src_mod:', src_mod)
    #print('trg_mod:', trg_mod)
    entry.tag_configure('modified', background='yellow')
    edited.tag_configure('modified', background='yellow')


def pop_up_control(sentence_count, corrected_sentence):
    # Create a Toplevel window

    top = tk.Toplevel(window)
    top.grid_rowconfigure(0, weight=1)

    tk.Label(top, text="Are sure that your corrected sentence (the one on the TOP) is semantically equivalent to the sentence shown below?"
                       "\nIf not, please go back to annotation screen (ESC) and make necessary changes.", font=("helvetica", "16"),
             justify=tk.CENTER, wraplength=1250, height=3, width=120, ).grid(row=0, columnspan=3)

    tk.Label(top, text="Your version", font=("helvetica", "16")).grid(row=1, )
    tf_entry_pop = tk.Text(top, height=5, font=("helvetica", "16"))
    tf_entry_pop.insert(0.0, corrected_sentence)
    tf_entry_pop.grid(row=1, column=1)

    tk.Label(top, text="Original annotator's version", font=("helvetica", "16")).grid(row=2)
    tf_human_pop = tk.Text(top, height=5, font=("helvetica", "16"))
    randomized_index = get_random_index()
    randomized_index = randomized_index % limit
    tf_human_pop.insert(0.0, human_corrected[randomized_index ])
    tf_human_pop.grid(row=2, column=1)

    # Create a Button to print something in the Entry widget
    # Create a Button Widget in the Toplevel Window
    button = tk.Button(top, text="Next", command=lambda: pop_up_annotate(top))
    button.grid(row=3, column=3)
    top.bind("<Return>", lambda x: pop_up_annotate(top))
    top.bind("<KP_Enter>", lambda x: pop_up_annotate(top))

    top.bind('<Escape>', lambda x: top.destroy())


def disable_rb(radiobuttons, selected):
    for key in radiobuttons:
        if key["text"] != selected:
            key["variable"] = None


def select_rb_key(vars_list, radiobuttons, selected):
    print(selected)
    vars_list[0].set("Incomprehensible")
    for key in radiobuttons:
        if key["text"] != selected:
            key["variable"] = None


def pop_up_annotate(prev_window):
    prev_window.destroy()
    top = tk.Toplevel(window)
    options = {
        "Grammaticality": [(1, "Incomprehensible"), (2, "Somewhat comprehensible"), (3, "Comprehensible"), (4, "Perfect"),
                           (0, "Other")],
        "Fluency": [(1, "Extremely unnatural"), (2, "Somewhat unnatural"), (3, "Somewhat natural"),
                    (4, "Extremely natural"),  (0, "Other")],
        "Meaning Preservation": [(1, "Substantially different"), (2, "Moderate differences"), (3, "Minor differences"),
                                 (4, "Identical"), (0, "Other")]}
    vars_list = []
    radiobuttons = defaultdict(list)

    for k, v in options.items():
        frame = tk.Frame(top)
        frame.pack()
        tk.Label(frame, text=k, font=("helvetica", "16")).pack()
        var = tk.StringVar()
        vars_list.append(var)
        for opt in v:
            rb = tk.Radiobutton(frame, text=opt[1], variable=var, value=f"{k},{opt[0]},{opt[1]}",
                                command=lambda k=k, selected=opt[1]: disable_rb(radiobuttons[k], selected))
            rb.pack(side="left")
            radiobuttons[k].append(rb)
    show = tk.Button(top, text="Next", command=lambda: check(top, [v.get().split(",") for v in vars_list]))
    show.pack()

    top.bind("1", lambda k: select_rb_key(vars_list, radiobuttons["Grammaticality"], options["Grammaticality"][0][1]))
    top.bind("2", lambda k: select_rb_key(radiobuttons["Grammaticality"], options["Grammaticality"][1][1]))
    top.bind("3", lambda k: select_rb_key(radiobuttons["Grammaticality"], options["Grammaticality"][2][1]))
    top.bind("4", lambda k: select_rb_key(radiobuttons["Grammaticality"], options["Grammaticality"][3][1]))
    top.bind("5", lambda k: select_rb_key(radiobuttons["Grammaticality"], options["Grammaticality"][4][1]))

    top.bind("<Return>", lambda x: check(top, [v.get().split(",") for v in vars_list]))
    top.bind("<KP_Enter>", lambda x: check(top, [v.get().split(",") for v in vars_list]))


def check(top, vars_list):
    selected = sum([v == [""] for v in vars_list])
    if selected > 0:
        top = tk.Toplevel(window)
        tk.Label(top, text="Please make sure you annotate everything", font=("helvetica", "14")).pack(side="left")
        show = tk.Button(top, text="Next", command=lambda: top.destroy())
        top.bind("<Return>", lambda x: top.destroy())
        top.bind("<KP_Enter>", lambda x: top.destroy())
        top.bind('<Escape>', lambda x: top.destroy())

        show.pack()
    else:
        save_and_next(top, vars_list)


def save_and_next(top, vars_list):
    top.destroy()
    global sentence_count
    corrected_sentence = tf_entry.get("1.0", "end").strip()
    annotation = {
        "system": seen_extensions[int(randomized_order[sentence_count]/limit)],
        "sentence-no": int(randomized_order[sentence_count]%limit),
        "system_prediction": tf_model.get("1.0", "end").strip(),
        "corrected_prediction": corrected_sentence,
        "human_reference": human_corrected[int(randomized_order[sentence_count]%limit)]
    }
    annotation.update({v[0]: f"{v[1]} ({v[2]})" for v in vars_list})
    if len(annotations) > sentence_count:
        annotations[sentence_count] = annotation
    else:
        annotations.append(annotation)
    save()
    if sentence_count < limit:
        sentence_count += 1
        label_counter["text"] = counter_text % (sentence_count+1, limit)
        reset(sentence_count)
    if sentence_count == limit:
        next["text"] = "Finish"


def get_next():
    global sentence_count
    corrected_sentence = tf_entry.get("1.0", "end").strip()
    pop_up_control(sentence_count, corrected_sentence)


def get_prev():
    global sentence_count
    if sentence_count != 1:
        sentence_count -= 1
        label_counter["text"] = counter_text % (sentence_count+1, limit)
        reset(sentence_count)


window = tk.Tk()

label_counter = tk.Label(text=counter_text % (sentence_count+1, limit))

label_model = tk.Label(text="Automatically corrected sentence")
tf_model = tk.Text(window, **tf_config)

# input_variable = tk.StringVar(window)
label_entry = tk.Label(window, text="Make your corrections below.")
tf_entry = tk.Text(window, **tf_config)

label_human = tk.Label(window, text="Use the \"show/hide\" to see the human corrected version")
tf_human = tk.Text(window, **tf_config)
tf_human.config(state=tk.DISABLED)

tf_entry.bind("<Key>", lambda x: edit_text(tf_model, tf_entry))


show = tk.Button(window, text="Show/hide", command=lambda: hide_widget(tf_human))

next = tk.Button(window, text="Next", command=get_next, font=("helvetica", "18"))
prev = tk.Button(window, text="Previous", command=get_prev, font=("helvetica", "18"))

reset(sentence_count)
## packing
label_counter.pack()
label_model.pack()
tf_model.pack(fill="both", expand=True)
label_entry.pack()
tf_entry.pack(fill="both", expand=True)
label_human.pack()
tf_human.pack(fill="both", expand=True)
show.pack()
prev.pack(side=tk.LEFT)
next.pack(side=tk.RIGHT)
window.geometry("2000x500")
window.bind("<Return>", lambda x: get_next())
window.bind("<KP_Enter>", lambda x: get_next())

window.mainloop()
