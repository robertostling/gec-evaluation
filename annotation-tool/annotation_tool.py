import os
import tkinter as tk
import json

### files ###
from collections import defaultdict

show_it = True
sentence_count = 1
filename = ""
counter_text = "Sentence %i/%i"
tf_config = {"height": 0.1, "width": 100, "font": ("Arial", "24"), "wrap": "word" }
data_dir = "playing"
model_output_file = "../data/playing/Nyberg.CEFR_ABC.dev.orig.0-100"
human_corrected_file = "../data/playing/Nyberg.CEFR_ABC.dev.corr.0-100"

model_outputs = [l.strip() for l in open(model_output_file, "r").readlines()]
human_corrected = [l.strip() for l in open(human_corrected_file, "r").readlines()]
assert len(model_outputs) == len(human_corrected)
limit = len(model_outputs)

output_file_name = model_output_file + ".json"

if os.path.exists(output_file_name):
    annotations = json.load(open(output_file_name))
    sentence_count = len(annotations) + 1
else:
    annotations = []


###

# Functions
def hide_widget(widget):
    global show_it
    widget.config(state=tk.NORMAL)
    if show_it:
        widget.insert(0.0, human_corrected[sentence_count - 1])
        show_it = False
    else:
        widget.delete(0.0, "end")
        show_it = True
    widget.config(state=tk.DISABLED)


def reset(sentence_count):
    tf_human.config(state=tk.NORMAL)
    tf_model.delete(0.0,"end")
    tf_human.delete(0.0, "end")
    tf_entry.delete(0.0, "end")
    tf_model.insert(0.0, model_outputs[sentence_count-1])
    tf_human.config(state=tk.DISABLED)

    if len(annotations) >= sentence_count:
        tf_entry.insert(0.0, annotations[sentence_count - 1])
    else:
        tf_entry.insert(0.0, model_outputs[sentence_count - 1])

    global show_it
    show_it = True


def save():
    output_file = open(output_file_name, 'w', encoding='utf-8')
    x = json.dumps(annotations, indent=2)
    output_file.write(
        x
    )
    if False:
        for dic in annotations:
            json.dump(dic, output_file)
            output_file.write("\n")


def pop_up(sentence_count, corrected_sentence):

    # Create a Toplevel window
    top = tk.Toplevel(window)
    top.geometry("750x250")

    tf_entry_pop = tk.Text(top, **tf_config)
    tf_entry_pop.insert(0.0, corrected_sentence)

    tf_human_pop = tk.Text(top, **tf_config)
    tf_human_pop.insert(0.0, human_corrected[sentence_count-1])

    tf_entry_pop.pack(fill="both", expand=True)
    tf_human_pop.pack(fill="both", expand=True)

    # Create a Button to print something in the Entry widget
    # Create a Button Widget in the Toplevel Window
    button = tk.Button(top, text="Yes", command=lambda: pop_up_annotate(top))
    button.pack(pady=5, side=tk.TOP)
    button.bind("<Enter>")


def disable_rb(radiobuttons, selected):

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
                    (4, "Extremely natural")],
        "Meaning": [(1, "Substantially different"), (2, "Moderate differences"), (3, "Minor differences"),
                    (4, "Identical"), (0, "Other")]}
    vars_list = []
    radiobuttons = defaultdict(list)

    for k, v in options.items():
        frame = tk.Frame(top)
        frame.pack()
        tk.Label(frame, text=k, font=("arial", "20")).pack(side="left")
        var = tk.StringVar()
        vars_list.append(var)
        for opt in v:
            rb = tk.Radiobutton(frame, text=opt[1], variable=var, value=f"{k},{opt[0]},{opt[1]}", command=lambda k=k,selected=opt[1]: disable_rb(radiobuttons[k], selected))
            rb.pack(side="left")
            radiobuttons[k].append(rb)

    show = tk.Button(top, text="Next", command=lambda: check(top, [v.get().split(",") for v in vars_list]))
    show.pack()


def check(top, vars_list):
    selected = sum([v == "" for v in vars_list])
    if selected > 0:
        top = tk.Toplevel(window)
        tk.Label(top, text="Please make sure you annotate everything", font=("arial", "20")).pack(side="left")
        show = tk.Button(top, text="Next", command=lambda: top.destroy())
        show.pack()
    else:
        save_and_next(top, vars_list)


def save_and_next(top, vars_list):
    top.destroy()
    global sentence_count
    corrected_sentence = tf_entry.get("1.0", "end").strip()
    annotation = {
            "system_prediction": model_outputs[sentence_count-1],
            "corrected_prediction": corrected_sentence,
            "human_reference": human_corrected[sentence_count-1],
        }
    annotation.update({v[0]: f"{v[1]} ({v[2]})" for v in vars_list})
    if len(annotations) >= sentence_count:
        annotations[sentence_count - 1] = annotation
    else:
        annotations.append(annotation)
    save()
    if sentence_count < limit:
        sentence_count += 1
        label_counter["text"] = counter_text % (sentence_count, limit)
        reset(sentence_count)
    if sentence_count == limit:
        next["text"] = "Finish"
        next["command"] = save


def get_next():

    global sentence_count
    corrected_sentence = tf_entry.get("1.0", "end").strip()
    pop_up(sentence_count, corrected_sentence)


def get_prev():
    global sentence_count
    if sentence_count != 1:
        sentence_count -= 1
        label_counter["text"] = counter_text % (sentence_count, limit)
        reset(sentence_count)


window = tk.Tk()

label_counter = tk.Label(text=counter_text % (sentence_count, limit))

label_model = tk.Label(text="Automatically corrected sentence")
tf_model = tk.Text(window,    **tf_config)

#input_variable = tk.StringVar(window)
label_entry = tk.Label(window, text="Make your corrections below.")
tf_entry = tk.Text(window, **tf_config)

label_human = tk.Label(window, text="Use the \"show/hide\" to see the human corrected version")
tf_human = tk.Text(window, **tf_config)
tf_human.config(state=tk.DISABLED)

show = tk.Button(window, text="Show/hide", command=lambda: hide_widget(tf_human))

next = tk.Button(window, text="Next", command=get_next, font= ("Arial", "24"))
prev = tk.Button(window, text="Previous", command=get_prev,  font= ("Arial", "24"))

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
window.mainloop()


