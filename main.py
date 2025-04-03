import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class CampaignApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Campanhas")
        self.root.geometry("1400x900")  # Janela maior

        # Dicionários para armazenar os dados
        self.file_campaigns = {}       # Campanhas carregadas do arquivo (ex.: campanhas.json)
        self.added_campaigns = {}      # Campanhas criadas nesta sessão
        self.historic_campaigns = {}   # Campanhas carregadas do histórico (campanhas_historico.json)
        self.monsters = {}             # Dados do arquivo monstros.json
        self.items = {}                # Dados do arquivo itens.json

        self.modified_file_campaigns = set()  # Títulos de campanhas do arquivo que foram editadas

        self.campaign_file_path = None

        # Campos da campanha
        self.fields = [
            "id", "titulo", "imagem", "dificuldade", "grupoMinimo", "localidade",
            "corpo", "monstros", "chefões", "recompensas", "npcs"
        ]
        self.numeric_fields = ["grupoMinimo"]
        # Para campos que podem ter múltiplas linhas (listas ou textos mais longos)
        self.list_fields = ["corpo", "monstros", "chefões", "recompensas", "npcs"]

        self.entries = {}     # Widgets de entrada do formulário
        self.check_vars = {}  # Variáveis dos checkbuttons

        # Carrega histórico e outros arquivos (se existirem)
        self.load_history()
        self.load_monsters()
        self.load_items()

        self.setup_ui()

        # Ao fechar, salvar o histórico
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_history(self):
        """Carrega o arquivo campanhas_historico.json (se existir); caso contrário, inicia com vazio."""
        if os.path.exists("campanhas_historico.json"):
            try:
                with open("campanhas_historico.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for camp in data:
                        if "titulo" in camp:
                            self.historic_campaigns[camp["titulo"]] = camp
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o histórico de campanhas: {e}")
        else:
            self.historic_campaigns = {}

    def load_monsters(self):
        """Carrega os dados do arquivo monstros.json (se existir)."""
        if os.path.exists("monstros.json"):
            try:
                with open("monstros.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for m in data:
                        if "nome" in m:
                            self.monsters[m["nome"]] = m
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar monstros: {e}")
        else:
            self.monsters = {}

    def load_items(self):
        """Carrega os dados do arquivo itens.json (se existir)."""
        if os.path.exists("itens.json"):
            try:
                with open("itens.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for it in data:
                        if "nome" in it:
                            self.items[it["nome"]] = it
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar itens: {e}")
        else:
            self.items = {}

    def setup_ui(self):
        # Header: seleção de arquivo de campanhas
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        btn_select = ttk.Button(top_frame, text="Selecionar Arquivo de Campanhas (.json)", command=self.select_file)
        btn_select.pack(side=tk.LEFT)
        self.file_label = ttk.Label(top_frame, text="Nenhum arquivo selecionado")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Frame principal: formulário à esquerda e Notebook à direita
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Formulário para dados da campanha
        form_frame = ttk.LabelFrame(main_frame, text="Dados da Campanha")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        canvas = tk.Canvas(form_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.form_inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.form_inner, anchor="nw")
        self.form_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas)))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        for idx, field in enumerate(self.fields):
            lbl = ttk.Label(self.form_inner, text=field)
            lbl.grid(row=idx, column=0, sticky=tk.W, padx=5, pady=2)
            if field in self.list_fields:
                txt = tk.Text(self.form_inner, height=3, width=40)
                txt.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=2)
                self.entries[field] = txt
            else:
                ent = ttk.Entry(self.form_inner, width=40)
                ent.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=2)
                self.entries[field] = ent
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.form_inner, text="Não tem", variable=var,
                                   command=lambda f=field, v=var: self.toggle_field(f, v))
            chk.grid(row=idx, column=2, padx=5, pady=2)
            self.check_vars[field] = var

        # Notebook com 5 abas:
        # 1. Campanhas do Arquivo, 2. Campanhas Adicionadas, 3. Histórico de Campanhas,
        # 4. Monstros, 5. Itens.
        notebook = ttk.Notebook(main_frame)
        notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba 1: Campanhas do Arquivo
        self.tab_file = ttk.Frame(notebook)
        notebook.add(self.tab_file, text="Campanhas do Arquivo")
        self.file_campaign_listbox = tk.Listbox(self.tab_file, width=40)
        self.file_campaign_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_campaign_listbox.bind("<Double-Button-1>", lambda e: self.edit_campaign_popup("file"))
        file_button_frame = ttk.Frame(self.tab_file)
        file_button_frame.pack(fill=tk.X, padx=5, pady=5)
        btn_del_file = ttk.Button(file_button_frame, text="Excluir", command=self.delete_campaign_from_file)
        btn_del_file.pack(side=tk.LEFT, padx=5)

        # Aba 2: Campanhas Adicionadas (sessão atual)
        self.tab_added = ttk.Frame(notebook)
        notebook.add(self.tab_added, text="Campanhas Adicionadas")
        self.added_campaign_listbox = tk.Listbox(self.tab_added, width=40)
        self.added_campaign_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.added_campaign_listbox.bind("<Double-Button-1>", lambda e: self.edit_campaign_popup("added"))
        added_button_frame = ttk.Frame(self.tab_added)
        added_button_frame.pack(fill=tk.X, padx=5, pady=5)
        btn_del_added = ttk.Button(added_button_frame, text="Excluir", command=self.delete_campaign_from_added)
        btn_del_added.pack(side=tk.LEFT, padx=5)

        # Aba 3: Histórico de Campanhas
        self.tab_history = ttk.Frame(notebook)
        notebook.add(self.tab_history, text="Histórico de Campanhas")
        self.history_campaign_listbox = tk.Listbox(self.tab_history, width=40)
        self.history_campaign_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_campaign_listbox.bind("<Double-Button-1>", lambda e: self.edit_campaign_popup("history"))
        history_button_frame = ttk.Frame(self.tab_history)
        history_button_frame.pack(fill=tk.X, padx=5, pady=5)
        btn_del_history = ttk.Button(history_button_frame, text="Excluir", command=self.delete_campaign_from_history)
        btn_del_history.pack(side=tk.LEFT, padx=5)

        # Aba 4: Monstros (importação para o campo "monstros")
        self.tab_monsters = ttk.Frame(notebook)
        notebook.add(self.tab_monsters, text="Monstros")
        self.monster_listbox = tk.Listbox(self.tab_monsters, width=40)
        self.monster_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.monster_listbox.bind("<Double-Button-1>", lambda e: self.show_detail_popup("monster"))
        monster_button_frame = ttk.Frame(self.tab_monsters)
        monster_button_frame.pack(fill=tk.X, padx=5, pady=5)
        btn_import_monster = ttk.Button(monster_button_frame, text="Importar para Campanha", command=lambda: self.import_monster_to_campaign(individual=True))
        btn_import_monster.pack(side=tk.LEFT, padx=5)
        btn_import_all_monsters = ttk.Button(monster_button_frame, text="Importar Todos", command=lambda: self.import_monster_to_campaign(individual=False))
        btn_import_all_monsters.pack(side=tk.LEFT, padx=5)

        # Aba 5: Itens (importação para o campo "recompensas")
        self.tab_items = ttk.Frame(notebook)
        notebook.add(self.tab_items, text="Itens")
        self.item_listbox = tk.Listbox(self.tab_items, width=40)
        self.item_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.item_listbox.bind("<Double-Button-1>", lambda e: self.show_detail_popup("item"))
        item_button_frame = ttk.Frame(self.tab_items)
        item_button_frame.pack(fill=tk.X, padx=5, pady=5)
        btn_import_item = ttk.Button(item_button_frame, text="Importar para Campanha", command=lambda: self.import_item_to_campaign(individual=True))
        btn_import_item.pack(side=tk.LEFT, padx=5)
        btn_import_all_items = ttk.Button(item_button_frame, text="Importar Todos", command=lambda: self.import_item_to_campaign(individual=False))
        btn_import_all_items.pack(side=tk.LEFT, padx=5)

        # Frame inferior: botões para adicionar campanha e gerar arquivo
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        btn_add = ttk.Button(bottom_frame, text="Adicionar Campanha", command=self.add_campaign)
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_generate = ttk.Button(bottom_frame, text="Gerar Arquivo", command=self.generate_file)
        btn_generate.pack(side=tk.LEFT, padx=5)

        self.update_listboxes()

    def _on_mousewheel(self, event, canvas):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def toggle_field(self, field, var):
        widget = self.entries[field]
        default = "0" if field in self.numeric_fields else "nenhum"
        if var.get():
            if field in self.list_fields:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, default)
                widget.config(state=tk.DISABLED)
            else:
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)
                widget.insert(0, default)
                widget.config(state="disabled")
        else:
            if field in self.list_fields:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
            else:
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)

    def add_campaign(self):
        camp = {}
        for field in self.fields:
            widget = self.entries[field]
            if field in self.list_fields:
                if self.check_vars[field].get():
                    value = "nenhum"
                else:
                    value = widget.get("1.0", tk.END).strip()
            else:
                if self.check_vars[field].get():
                    value = "0" if field in self.numeric_fields else "nenhum"
                else:
                    value = widget.get().strip()
            camp[field] = value
        if not camp.get("titulo") or camp["titulo"] == "nenhum":
            messagebox.showerror("Erro", "O campo 'titulo' é obrigatório.")
            return
        self.added_campaigns[camp["titulo"]] = camp
        self.update_listboxes()
        messagebox.showinfo("Sucesso", f"Campanha '{camp['titulo']}' adicionada com sucesso!")
        self.clear_form()

    def update_listboxes(self):
        self.file_campaign_listbox.delete(0, tk.END)
        for name in self.file_campaigns:
            self.file_campaign_listbox.insert(tk.END, name)
        self.added_campaign_listbox.delete(0, tk.END)
        for name in self.added_campaigns:
            self.added_campaign_listbox.insert(tk.END, name)
        self.history_campaign_listbox.delete(0, tk.END)
        for name in self.historic_campaigns:
            self.history_campaign_listbox.insert(tk.END, name)
        self.monster_listbox.delete(0, tk.END)
        for name in self.monsters:
            self.monster_listbox.insert(tk.END, name)
        self.item_listbox.delete(0, tk.END)
        for name in self.items:
            self.item_listbox.insert(tk.END, name)

    def clear_form(self):
        for field in self.fields:
            widget = self.entries[field]
            if field in self.list_fields:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
            else:
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)
            self.check_vars[field].set(False)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.campaign_file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.load_file_campaigns()
        else:
            self.file_label.config(text="Nenhum arquivo selecionado")

    def load_file_campaigns(self):
        try:
            with open(self.campaign_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.file_campaigns = {}
                for camp in data:
                    if "titulo" in camp:
                        self.file_campaigns[camp["titulo"]] = camp
            else:
                if "titulo" in data:
                    self.file_campaigns = {data["titulo"]: data}
                else:
                    self.file_campaigns = {}
            self.update_listboxes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar campanhas do arquivo: {e}")

    def edit_campaign_popup(self, source):
        if source == "file":
            selection = self.file_campaign_listbox.curselection()
            if not selection:
                return
            name = self.file_campaign_listbox.get(selection[0])
            camp = self.file_campaigns[name]
        elif source == "added":
            selection = self.added_campaign_listbox.curselection()
            if not selection:
                return
            name = self.added_campaign_listbox.get(selection[0])
            camp = self.added_campaigns[name]
        elif source == "history":
            selection = self.history_campaign_listbox.curselection()
            if not selection:
                return
            name = self.history_campaign_listbox.get(selection[0])
            camp = self.historic_campaigns[name]
        else:
            return
        popup = tk.Toplevel(self.root)
        popup.title(f"Editar Campanha - {name}")
        popup.geometry("600x600")
        canvas = tk.Canvas(popup)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas)))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        edit_entries = {}
        edit_check_vars = {}
        for idx, field in enumerate(self.fields):
            lbl = ttk.Label(frame, text=field)
            lbl.grid(row=idx, column=0, sticky=tk.W, padx=5, pady=2)
            if field in self.list_fields:
                txt = tk.Text(frame, height=3, width=40)
                txt.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=2)
                current_val = camp.get(field, "")
                txt.insert(tk.END, current_val)
                edit_entries[field] = txt
            else:
                ent = ttk.Entry(frame, width=40)
                ent.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=2)
                ent.insert(0, camp.get(field, ""))
                edit_entries[field] = ent
            var = tk.BooleanVar(value=(camp.get(field, "") == "nenhum" or camp.get(field, "") == "0"))
            chk = ttk.Checkbutton(frame, text="Não tem", variable=var,
                                  command=lambda f=field, v=var, key=field: self.toggle_field_edit(f, v, edit_entries, key))
            chk.grid(row=idx, column=2, padx=5, pady=2)
            edit_check_vars[field] = var

        def save_changes():
            for field in self.fields:
                widget = edit_entries[field]
                if field in self.list_fields:
                    if edit_check_vars[field].get():
                        value = "nenhum"
                    else:
                        value = widget.get("1.0", tk.END).strip()
                else:
                    if edit_check_vars[field].get():
                        value = "0" if field in self.numeric_fields else "nenhum"
                    else:
                        value = widget.get().strip()
                camp[field] = value
            if source == "file":
                self.modified_file_campaigns.add(name)
            self.update_listboxes()
            messagebox.showinfo("Sucesso", f"Campanha '{name}' atualizada com sucesso!")
            popup.destroy()

        btn_save = ttk.Button(frame, text="Salvar Alterações", command=save_changes)
        btn_save.grid(row=len(self.fields), column=0, columnspan=3, pady=10)

    def toggle_field_edit(self, field, var, entries, key):
        widget = entries[key]
        default = "0" if field in self.numeric_fields else "nenhum"
        if var.get():
            if field in self.list_fields:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, default)
                widget.config(state=tk.DISABLED)
            else:
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)
                widget.insert(0, default)
                widget.config(state="disabled")
        else:
            if field in self.list_fields:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
            else:
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)

    def delete_campaign_from_file(self):
        selection = self.file_campaign_listbox.curselection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma campanha para excluir.")
            return
        name = self.file_campaign_listbox.get(selection[0])
        if messagebox.askyesno("Confirmação", f"Excluir a campanha '{name}' do arquivo atual?"):
            if name in self.file_campaigns:
                del self.file_campaigns[name]
            if name in self.modified_file_campaigns:
                self.modified_file_campaigns.remove(name)
            self.update_listboxes()

    def delete_campaign_from_added(self):
        selection = self.added_campaign_listbox.curselection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma campanha para excluir dos adicionados.")
            return
        name = self.added_campaign_listbox.get(selection[0])
        if messagebox.askyesno("Confirmação", f"Excluir a campanha '{name}' dos adicionados?"):
            if name in self.added_campaigns:
                del self.added_campaigns[name]
            self.update_listboxes()

    def delete_campaign_from_history(self):
        selection = self.history_campaign_listbox.curselection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma campanha para excluir do histórico.")
            return
        name = self.history_campaign_listbox.get(selection[0])
        if messagebox.askyesno("Confirmação", f"Excluir a campanha '{name}' do histórico?"):
            if name in self.historic_campaigns:
                del self.historic_campaigns[name]
            self.update_listboxes()

    def import_monster_to_campaign(self, individual=True):
        if individual:
            selection = self.monster_listbox.curselection()
            if not selection:
                messagebox.showerror("Erro", "Selecione um monstro para importar.")
                return
            name = self.monster_listbox.get(selection[0])
            current = self.entries["monstros"].get("1.0", tk.END).strip()
            new_val = current + ("\n" if current else "") + name
            self.entries["monstros"].delete("1.0", tk.END)
            self.entries["monstros"].insert(tk.END, new_val)
        else:
            names = list(self.monsters.keys())
            current = self.entries["monstros"].get("1.0", tk.END).strip()
            for n in names:
                current += "\n" + n if current else n
            self.entries["monstros"].delete("1.0", tk.END)
            self.entries["monstros"].insert(tk.END, current)
        messagebox.showinfo("Sucesso", "Monstro(s) importado(s) para a campanha.")

    def import_item_to_campaign(self, individual=True):
        if individual:
            selection = self.item_listbox.curselection()
            if not selection:
                messagebox.showerror("Erro", "Selecione um item para importar.")
                return
            name = self.item_listbox.get(selection[0])
            current = self.entries["recompensas"].get("1.0", tk.END).strip()
            new_val = current + ("\n" if current else "") + name
            self.entries["recompensas"].delete("1.0", tk.END)
            self.entries["recompensas"].insert(tk.END, new_val)
        else:
            names = list(self.items.keys())
            current = self.entries["recompensas"].get("1.0", tk.END).strip()
            for n in names:
                current += "\n" + n if current else n
            self.entries["recompensas"].delete("1.0", tk.END)
            self.entries["recompensas"].insert(tk.END, current)
        messagebox.showinfo("Sucesso", "Item(s) importado(s) para a campanha.")

    def show_detail_popup(self, source):
        if source == "monster":
            selection = self.monster_listbox.curselection()
            if not selection:
                return
            name = self.monster_listbox.get(selection[0])
            detail = self.monsters.get(name, {})
        elif source == "item":
            selection = self.item_listbox.curselection()
            if not selection:
                return
            name = self.item_listbox.get(selection[0])
            detail = self.items.get(name, {})
        else:
            return
        popup = tk.Toplevel(self.root)
        popup.title(f"Detalhes - {name}")
        text = tk.Text(popup, wrap=tk.WORD, width=60, height=20)
        text.pack(fill=tk.BOTH, expand=True)
        detail_str = json.dumps(detail, indent=4, ensure_ascii=False)
        text.insert(tk.END, detail_str)
        text.config(state=tk.DISABLED)

    def generate_file(self):
        summary = "Resumo das alterações:\n\n"
        if self.modified_file_campaigns:
            summary += "Campanhas modificadas (do arquivo):\n"
            for name in self.modified_file_campaigns:
                summary += f" - {name}\n"
        if self.added_campaigns:
            summary += "\nCampanhas adicionadas:\n"
            for name in self.added_campaigns:
                summary += f" - {name}\n"
        summary += "\nDeseja gerar o novo arquivo de campanhas?\n\n"
        summary += ("Observação: O arquivo original não será alterado; um novo arquivo 'campanhas_novo.json' será criado com as alterações e adições.")
        if not messagebox.askyesno("Confirmar Geração de Arquivo", summary):
            return
        try:
            with open(self.campaign_file_path, "r", encoding="utf-8") as f:
                original_data = json.load(f)
            if not isinstance(original_data, list):
                original_data = [original_data]
            for i, camp in enumerate(original_data):
                if camp.get("titulo") in self.modified_file_campaigns:
                    original_data[i] = self.file_campaigns[camp.get("titulo")]
            for name, camp in self.added_campaigns.items():
                if not any(c.get("titulo") == name for c in original_data):
                    original_data.append(camp)
            base, ext = os.path.splitext(self.campaign_file_path)
            new_file_path = f"{base}_novo{ext}"
            with open(new_file_path, "w", encoding="utf-8") as f:
                json.dump(original_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Sucesso", f"Novo arquivo gerado: {os.path.basename(new_file_path)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar novo arquivo: {e}")

    def on_closing(self):
        # Mescla as campanhas adicionadas com o histórico e salva
        for name, camp in self.added_campaigns.items():
            self.historic_campaigns[name] = camp
        try:
            with open("campanhas_historico.json", "w", encoding="utf-8") as f:
                json.dump(list(self.historic_campaigns.values()), f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o histórico: {e}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CampaignApp(root)
    root.mainloop()
