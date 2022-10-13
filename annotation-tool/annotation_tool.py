import os
import tkinter as tk
import tkinter.ttk as ttk


### files ###

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

output_file_name = model_output_file + ".ann"

if os.path.exists(output_file_name):
    annotations = [l.strip() for l in open(output_file_name, "r").readlines()]
    sentence_count = len(annotations) + 1
else:
    annotations = []


###

# Functions
def hide_widget(widget):
    global show_it
    if show_it:
        widget.pack(fill="both", expand=True)
        show_it = False
    else:
        widget.pack_forget()
        show_it = True


def reset(sentence_count):
    tf_human.config(state=tk.NORMAL)
    tf_model.delete(0.0,"end")
    tf_human.delete(0.0, "end")
    tf_entry.delete(0.0, "end")
    tf_model.insert(0.0, model_outputs[sentence_count-1])
    tf_human.insert(0.0, human_corrected[sentence_count - 1])

    if len(annotations) >= sentence_count:
        tf_entry.insert(0.0, annotations[sentence_count - 1])
    else:
        tf_entry.insert(0.0, model_outputs[sentence_count - 1])

    tf_human.config(state=tk.DISABLED)
    tf_human.pack_forget()
    global show_it
    show_it = True


def save():
    output_file = open(output_file_name, "w", encoding="utf-8")
    for ann in annotations:
        output_file.write(ann + "\n")


def get_next():
    global sentence_count, input_variable
    corrected_sentence = tf_entry.get("1.0", "end").strip()
    if len(annotations) >= sentence_count:
        annotations[sentence_count-1] = corrected_sentence
    else:
        annotations.append(corrected_sentence)
    save()
    if sentence_count < limit:
        sentence_count += 1
        label_counter["text"] = counter_text % (sentence_count, limit)
        reset(sentence_count)
    if sentence_count == limit:
        next["text"] = "Finish"
        next["command"] = save


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
label_entry = tk.Label(window, text="Enter your corrected sentence here.")
tf_entry = tk.Text(window, **tf_config)

label_human = tk.Label(window, text="In case of emergency click the button to see the human corrected version")
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
show.pack()
prev.pack(side=tk.LEFT)
next.pack(side=tk.RIGHT)
window.geometry("2000x500")
window.mainloop()


