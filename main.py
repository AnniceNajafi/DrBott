import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
import os

# (Optional) If you have your LangChain + Ollama logic:
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Example template
base_template = """
Rewrite the question below in {num_variations} various ways, ensuring they have the same answer:

Question: "{question}"

Please list the variations in bullet points or separate them by new lines.
"""

# If you want to add advanced instructions (like preserve terms) you can incorporate them:
advanced_template = """
You are a helpful rewriting assistant. Follow these instructions exactly:

1. I want {num_variations} distinct rewrites of the question, each preserving the same meaning and answer.

2. If the user provides key terms in {key_terms}, then:
   - You MUST preserve them (exactly as they appear) in every variation.
   - All variations should include the key term.
   - Keep the same domain/context as the original question if it already uses those key terms.

3. If {key_terms} is empty or not provided:
   - Change the domain or context drastically (e.g., if it's about fishing, make it about parking a car, renting bikes, etc.).
   - Ensure the numbers and logic remain consistent but the scenario is totally different.

4. Do NOT provide or hallucinate the answer to the question. Only rewrite the question.

5. Temperature: {temperature}; Top_P: {top_p}.

6. Return the {num_variations} rewrites in bullet points or separate lines.

Here is the original question:
"{question}"

Now follow the rules above.

Please list the variations in bullet points or separate them by new lines.
"""

# Create an Ollama LLM with a default model
model = OllamaLLM(model="llama3")  # adjust "llama3" to the local model name

def create_gui():
    root = tk.Tk()
    root.title("Exam Question Variation Generator Pro")

    # -- Window background color --
    root.configure(bg="#FFDAB9")  # Pastel orange

    # -- Add Logo (optional) --
    try:
        pil_image = Image.open("peach-removebg.png")  # or the path to your logo
        # Optionally resize:
        pil_image = pil_image.resize((80, 50))
        logo_image = ImageTk.PhotoImage(pil_image)
        logo_label = tk.Label(root, image=logo_image, bg="#FFDAB9")
        logo_label.image = logo_image  # keep a reference
        logo_label.pack(pady=5)
    except Exception as e:
        print(f"Could not load logo: {e}")

    # -------------------------------
    # Main Frame to hold everything
    # -------------------------------
    main_frame = tk.Frame(root, bg="#FFDAB9")
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # 1) BASIC OPTIONS
    question_label = tk.Label(
        main_frame, 
        text="Enter your original question:", 
        bg="#FFDAB9"
    )
    question_label.grid(row=0, column=0, sticky="w")

    question_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=4)
    question_text.grid(row=1, column=0, columnspan=2, pady=5, sticky="we")

    variations_label = tk.Label(
        main_frame, 
        text="Number of variations:", 
        bg="#FFDAB9"
    )
    variations_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

    variations_entry = tk.Entry(main_frame)
    variations_entry.insert(0, "5")  # default value
    variations_entry.grid(row=3, column=0, sticky="we")

    # 2) ADVANCED OPTIONS FRAME (initially hidden)
    advanced_frame = tk.LabelFrame(
        main_frame, 
        text="Advanced Options", 
        bg="#FFDAB9", 
        fg="black", 
        bd=2, 
        relief=tk.GROOVE
    )
    advanced_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky="we")
    advanced_frame.grid_remove()  # hide initially

    # -- Key Terms --
    key_terms_label = tk.Label(advanced_frame, text="Preserve Key Terms:", bg="#FFDAB9")
    key_terms_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))

    key_terms_entry = tk.Entry(advanced_frame)
    key_terms_entry.grid(row=1, column=0, columnspan=2, sticky="we", padx=5)

    # -- Temperature --
    temp_label = tk.Label(advanced_frame, text="Temperature (0.0 - 1.0):", bg="#FFDAB9")
    temp_label.grid(row=2, column=0, sticky="w", padx=5, pady=(5, 0))

    temperature_entry = tk.Entry(advanced_frame)
    temperature_entry.insert(0, "0")
    temperature_entry.grid(row=3, column=0, sticky="we", padx=5)

    # -- Top_p --
    top_p_label = tk.Label(advanced_frame, text="Top_p (0.0 - 1.0):", bg="#FFDAB9")
    top_p_label.grid(row=2, column=1, sticky="w", padx=5, pady=(5, 0))

    top_p_entry = tk.Entry(advanced_frame)
    top_p_entry.insert(0, "0")
    top_p_entry.grid(row=3, column=1, sticky="we", padx=5)

    # Show/Hide advanced options with a Checkbox
    advanced_var = tk.BooleanVar(value=False)

    def toggle_advanced():
        if advanced_var.get():
            advanced_frame.grid()  # show
        else:
            advanced_frame.grid_remove()  # hide

    advanced_check = tk.Checkbutton(
        main_frame, 
        text="Show Advanced Options", 
        variable=advanced_var,
        bg="#FFDAB9",
        command=toggle_advanced
    )
    advanced_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

    # 3) Generate and Reset Buttons
    def generate_variations():
        # 3a) Get user inputs
        question = question_text.get("1.0", tk.END).strip()
        num_variations_str = variations_entry.get().strip()
        if not num_variations_str.isdigit():
            num_variations_str = "5"

        # If advanced options are shown, incorporate them
        if advanced_var.get():
            key_terms = key_terms_entry.get().strip()
            temperature_str = temperature_entry.get().strip()
            top_p_str = top_p_entry.get().strip()

            # Validate numeric input
            try:
                float(temperature_str)
            except:
                temperature_str = "0"
            try:
                float(top_p_str)
            except:
                top_p_str = "0"

            # Build the advanced prompt
            prompt_template = ChatPromptTemplate.from_template(advanced_template)
            chain = prompt_template | model

            response = chain.invoke({
                "question": question,
                "num_variations": num_variations_str,
                "key_terms": key_terms if key_terms else "None",
                "temperature": temperature_str,
                "top_p": top_p_str
            })

        else:
            # Basic template
            prompt_template = ChatPromptTemplate.from_template(base_template)
            chain = prompt_template | model

            response = chain.invoke({
                "question": question,
                "num_variations": num_variations_str
            })

        # 3b) Display output
        output_box.config(state=tk.NORMAL)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, response)
        output_box.config(state=tk.DISABLED)

    def reset_fields():
        question_text.delete("1.0", tk.END)
        variations_entry.delete(0, tk.END)
        variations_entry.insert(0, "5")

        key_terms_entry.delete(0, tk.END)
        temperature_entry.delete(0, tk.END)
        temperature_entry.insert(0, "0.7")
        top_p_entry.delete(0, tk.END)
        top_p_entry.insert(0, "1.0")

        # Clear output
        output_box.config(state=tk.NORMAL)
        output_box.delete("1.0", tk.END)
        output_box.config(state=tk.DISABLED)

    generate_button = tk.Button(
        main_frame,
        text="Generate Variations",
        command=generate_variations,
        bg="#FF8C00",  # dark orange
        fg="black"
    )
    generate_button.grid(row=6, column=0, sticky="w", pady=(5, 10))

    reset_button = tk.Button(
        main_frame,
        text="Reset Fields",
        command=reset_fields,
        bg="#FF8C00",
        fg="black"
    )
    reset_button.grid(row=6, column=1, sticky="e", pady=(5, 10))

    # 4) Output Box
    output_label = tk.Label(main_frame, text="Question Variations:", bg="#FFDAB9")
    output_label.grid(row=7, column=0, columnspan=2, sticky="w")

    output_box = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10)
    output_box.config(state=tk.DISABLED)
    output_box.grid(row=8, column=0, columnspan=2, pady=(5, 10), sticky="nsew")

    # 5) Save to File Button
    def save_to_file():
        content = output_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("No Content", "There is no text to save.")
            return

        # Show a "Save As" dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Variations saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    save_button = tk.Button(
        main_frame,
        text="Save to File",
        command=save_to_file,
        bg="#FF8C00",
        fg="black"
    )
    save_button.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    # Make columns/rows expand so the scrolledtext can fill space
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(8, weight=1)  # the output_box row

    root.mainloop()

if __name__ == "__main__":
    create_gui()
