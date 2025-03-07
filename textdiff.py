# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1msaXFJFv7_RqaRpsMVXwwAUt1uLpuQiJ
"""

!pip install pandas matplotlib japanize-matplotlib

import difflib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import japanize_matplotlib
import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
from pathlib import Path

class JapaneseTextDiffVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("日本文学テキスト差分可視化ツール")
        self.root.geometry("1000x800")

        self.texts = []
        self.text_names = []
        self.setup_ui()

    def setup_ui(self):
        # ファイル選択エリア
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(file_frame, text="テキストファイル:").pack(side="left")
        self.file_list = tk.Listbox(file_frame, width=50, height=5)
        self.file_list.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(side="left", padx=10)

        tk.Button(btn_frame, text="ファイル追加", command=self.add_file).pack(fill="x", pady=2)
        tk.Button(btn_frame, text="選択削除", command=self.remove_file).pack(fill="x", pady=2)
        tk.Button(btn_frame, text="全削除", command=self.clear_files).pack(fill="x", pady=2)

        # 可視化オプション
        option_frame = tk.Frame(self.root)
        option_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(option_frame, text="可視化タイプ:").pack(side="left")
        self.viz_type = tk.StringVar(value="colored_diff")
        tk.Radiobutton(option_frame, text="色付き差分表示", variable=self.viz_type,
                       value="colored_diff").pack(side="left", padx=5)
        tk.Radiobutton(option_frame, text="行ごとの差分統計", variable=self.viz_type,
                       value="line_stats").pack(side="left", padx=5)

        # 実行ボタン
        tk.Button(self.root, text="差分を可視化", command=self.visualize_diff).pack(pady=10)

        # 結果表示エリア
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("MS Gothic", 12))
        self.result_text.pack(fill="both", expand=True)
        self.result_text.config(state=tk.DISABLED)

    def add_file(self):
        filepaths = filedialog.askopenfilenames(
            title="テキストファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )

        for filepath in filepaths:
            if filepath:
                filename = os.path.basename(filepath)
                if filepath not in self.texts:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.texts.append(content)
                    self.text_names.append(filename)
                    self.file_list.insert(tk.END, filename)

    def remove_file(self):
        selected = self.file_list.curselection()
        if selected:
            idx = selected[0]
            self.file_list.delete(idx)
            self.texts.pop(idx)
            self.text_names.pop(idx)

    def clear_files(self):
        self.file_list.delete(0, tk.END)
        self.texts = []
        self.text_names = []

    def visualize_diff(self):
        if len(self.texts) < 2:
            self.update_result("少なくとも2つのファイルを選択してください。")
            return

        viz_type = self.viz_type.get()

        if viz_type == "colored_diff":
            self.show_colored_diff()
        elif viz_type == "line_stats":
            self.show_line_stats()

    def show_colored_diff(self):
        if len(self.texts) != 2:
            self.update_result("色付き差分表示は2つのファイルのみ対応しています。")
            return

        d = difflib.HtmlDiff()
        diff_html = d.make_file(
            self.texts[0].splitlines(),
            self.texts[1].splitlines(),
            self.text_names[0],
            self.text_names[1],
            context=True
        )

        # HTMLファイルに保存
        output_path = Path("text_diff.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(diff_html)

        # 結果を表示
        self.update_result(f"差分HTMLファイルを保存しました: {output_path.absolute()}\n"
                         f"ブラウザで開いて確認してください。\n\n"
                         f"緑色: 追加されたテキスト\n"
                         f"赤色: 削除されたテキスト")

    def show_line_stats(self):
        # 全テキストの行ごとの類似度を計算
        results = []

        for i in range(len(self.texts)):
            for j in range(i+1, len(self.texts)):
                text1_lines = self.texts[i].splitlines()
                text2_lines = self.texts[j].splitlines()

                # 行ごとの類似度を計算
                s = difflib.SequenceMatcher(None, text1_lines, text2_lines)
                ratio = s.ratio()

                # 差分を詳細に分析
                opcodes = s.get_opcodes()
                equal_count = sum(1 for tag, _, _, _, _ in opcodes if tag == 'equal')
                replace_count = sum(1 for tag, _, _, _, _ in opcodes if tag == 'replace')
                insert_count = sum(1 for tag, _, _, _, _ in opcodes if tag == 'insert')
                delete_count = sum(1 for tag, _, _, _, _ in opcodes if tag == 'delete')

                results.append({
                    'ファイル1': self.text_names[i],
                    'ファイル2': self.text_names[j],
                    '類似度': f"{ratio:.2%}",
                    '一致行数': equal_count,
                    '置換行数': replace_count,
                    '追加行数': insert_count,
                    '削除行数': delete_count
                })

        # 結果をテキストで表示
        output = "テキスト間の差分統計:\n\n"
        for r in results:
            output += f"■ {r['ファイル1']} と {r['ファイル2']} の比較:\n"
            output += f"  ・類似度: {r['類似度']}\n"
            output += f"  ・一致行数: {r['一致行数']}\n"
            output += f"  ・変更行数: {r['置換行数']} (置換)\n"
            output += f"  ・　　　　: {r['追加行数']} (追加)\n"
            output += f"  ・　　　　: {r['削除行数']} (削除)\n\n"

        self.update_result(output)

        # グラフも作成
        if len(results) > 0:
            self.create_similarity_graph(results)

    def create_similarity_graph(self, results):
        plt.figure(figsize=(10, 6))

        labels = [f"{r['ファイル1']}\nvs\n{r['ファイル2']}" for r in results]
        values = [float(r['類似度'].strip('%')) / 100 for r in results]

        plt.bar(labels, values, color='skyblue')
        plt.ylabel('類似度')
        plt.title('テキスト間の類似度比較')
        plt.ylim(0, 1)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for i, v in enumerate(values):
            plt.text(i, v + 0.02, f"{v:.2%}", ha='center')

        plt.tight_layout()
        plt.savefig('similarity_graph.png')
        plt.close()

        self.update_result(self.result_text.get(1.0, tk.END) +
                         "\n類似度グラフを保存しました: similarity_graph.png")

    def update_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = JapaneseTextDiffVisualizer(root)
    root.mainloop()