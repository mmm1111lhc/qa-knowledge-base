"""群问答知识库 · 学员提问/助教回答/老师补充"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from tkinter import messagebox
import time

from database import add_qa, search, delete_qa, update_qa, get_all_tags, count

# ── 主题 ──
ctk.set_appearance_mode("light")
BG = "#f5f2ed"
WHITE = "#ffffff"
ACCENT = "#4a90d9"
ACCENT_DARK = "#357abd"
TEXT = "#1f2328"
MUTED = "#888888"
CARD_BORDER = "#e0ddd8"

FONT_TITLE = ("PingFang SC", 18, "bold")
FONT_SECTION = ("PingFang SC", 14, "bold")
FONT_BODY = ("PingFang SC", 13)
FONT_MONO = ("Menlo", 11)


class QAKB:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("群问答知识库")
        self.root.geometry("900x680")
        self.root.minsize(760, 520)
        self.root.configure(fg_color=BG)

        self.selected_id = None

        # 布局
        self._build_layout()

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def _build_layout(self):
        # 左右分栏
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=0)
        main.grid_rowconfigure(0, weight=1)

        # ── 左侧：搜索 + 列表 ──
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.grid_rowconfigure(3, weight=1)

        # 标题
        ctk.CTkLabel(left, text="📚 群问答知识库",
                     font=FONT_TITLE, text_color=ACCENT
                     ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(left, text=f"共 {count()} 条问答",
                     font=("", 12), text_color=MUTED
                     ).grid(row=0, column=1, sticky="e", pady=(0, 6))
        left.grid_columnconfigure(1, weight=1)

        # 搜索行
        s = ctk.CTkFrame(left, fg_color=WHITE, corner_radius=8,
                         border_width=1, border_color=CARD_BORDER)
        s.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)
        s.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(s, text="🔍", font=("", 14)
                     ).grid(row=0, column=0, padx=(10, 4), pady=8)
        self.search_e = ctk.CTkEntry(s, font=FONT_BODY, height=34,
                                     fg_color="#f0ede8", border_width=0)
        self.search_e.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        self.search_e.bind("<Return>", lambda e: self._do_search())
        ctk.CTkButton(s, text="搜索", command=self._do_search,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      height=34, width=70, corner_radius=6,
                      text_color="white", font=("", 12, "bold")
                      ).grid(row=0, column=2, padx=(4, 10), pady=8)

        # 结果列表
        rf = ctk.CTkFrame(left, fg_color=WHITE, corner_radius=8,
                          border_width=1, border_color=CARD_BORDER)
        rf.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=4)
        rf.grid_rowconfigure(0, weight=1)
        rf.grid_columnconfigure(0, weight=1)
        self.result_list = ctk.CTkScrollableFrame(rf, fg_color="transparent")
        self.result_list.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.result_count = ctk.CTkLabel(left, text="",
                                         font=("", 12), text_color=MUTED)
        self.result_count.grid(row=3, column=0, columnspan=2, sticky="w")

        # ── 右侧：详情 ──
        right = ctk.CTkFrame(main, fg_color=WHITE, corner_radius=10,
                             border_width=1, border_color=CARD_BORDER,
                             width=360)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.grid_propagate(False)

        # 右侧内容滚动
        self.detail_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.detail_frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(self.detail_frame, text="点击左侧问答查看详情",
                     font=("", 13), text_color=MUTED).pack(pady=40)

        # ── 底部：新增 ──
        bottom = ctk.CTkFrame(self.root, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkButton(bottom, text="＋ 新增问答",
                      command=self._show_add_dialog,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      height=38, width=120, corner_radius=8,
                      text_color="white", font=("", 13, "bold")
                      ).pack(side="left")

        self._do_search()

    def _do_search(self):
        query = self.search_e.get().strip()
        results = search(query)
        self.result_count.configure(text=f"找到 {len(results)} 条结果")

        for w in self.result_list.winfo_children():
            w.destroy()

        for r in results:
            card = ctk.CTkFrame(self.result_list, fg_color="#f8f7f4",
                                corner_radius=8, height=50)
            card.pack(fill="x", pady=2)
            card.pack_propagate(False)

            q_text = r["question"][:60] + ("..." if len(r["question"]) > 60 else "")
            lbl = ctk.CTkLabel(card, text=f"❓ {q_text}",
                               font=FONT_BODY, anchor="w")
            lbl.pack(side="left", padx=10)

            tags = r.get("tags", [])
            if tags:
                tag_text = " ".join(f"#{t}" for t in tags[:2])
                ctk.CTkLabel(card, text=tag_text, font=("", 11),
                             text_color=ACCENT).pack(side="left", padx=4)

            has_ta = "✅" if r.get("ta_answer") else "⏳"
            has_t = "✅" if r.get("teacher_supplement") else "⏳"
            ctk.CTkLabel(card, text=f"助教{has_ta} 我{has_t}",
                         font=("", 11), text_color=MUTED
                         ).pack(side="right", padx=6)

            card.bind("<Button-1>", lambda e, rec=r: self._show_detail(rec))

    def _show_detail(self, rec):
        self.selected_id = rec["id"]
        for w in self.detail_frame.winfo_children():
            w.destroy()

        # 问题
        ctk.CTkLabel(self.detail_frame, text="❓ 问题",
                     font=FONT_SECTION, text_color=ACCENT
                     ).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(self.detail_frame, text=rec["question"],
                     font=FONT_BODY, wraplength=320, justify="left"
                     ).pack(anchor="w", pady=(0, 8))

        # 提问人
        if rec.get("asker"):
            ctk.CTkLabel(self.detail_frame,
                         text=f"提问人: {rec['asker']}",
                         font=("", 11), text_color=MUTED
                         ).pack(anchor="w", pady=(0, 8))

        # 标签
        if rec.get("tags"):
            ctk.CTkLabel(self.detail_frame,
                         text="🏷 " + " ".join(f"#{t}" for t in rec["tags"]),
                         font=("", 11), text_color=ACCENT
                         ).pack(anchor="w", pady=(0, 8))

        ctk.CTkFrame(self.detail_frame, fg_color=CARD_BORDER,
                     height=1).pack(fill="x", pady=4)

        # 助教回答
        ctk.CTkLabel(self.detail_frame, text="👩‍🏫 助教回答",
                     font=FONT_SECTION, text_color="#5a8f5a"
                     ).pack(anchor="w", pady=(4, 2))
        ta_text = rec.get("ta_answer") or "（暂未回答）"
        ta_color = TEXT if rec.get("ta_answer") else MUTED
        self.ta_e = ctk.CTkTextbox(self.detail_frame, font=FONT_BODY,
                                   height=60, fg_color="#f0ede8",
                                   border_width=0, corner_radius=6,
                                   text_color=ta_color)
        self.ta_e.insert("1.0", ta_text)
        self.ta_e.pack(fill="x", pady=(0, 4))

        ctk.CTkFrame(self.detail_frame, fg_color=CARD_BORDER,
                     height=1).pack(fill="x", pady=4)

        # 老师补充
        ctk.CTkLabel(self.detail_frame, text="👨‍🏫 我的补充",
                     font=FONT_SECTION, text_color="#c97a3a"
                     ).pack(anchor="w", pady=(4, 2))
        sup_text = rec.get("teacher_supplement") or "（暂未补充）"
        sup_color = TEXT if rec.get("teacher_supplement") else MUTED
        self.sup_e = ctk.CTkTextbox(self.detail_frame, font=FONT_BODY,
                                    height=60, fg_color="#f0ede8",
                                    border_width=0, corner_radius=6,
                                    text_color=sup_color)
        self.sup_e.insert("1.0", sup_text)
        self.sup_e.pack(fill="x", pady=(0, 4))

        # 操作按钮
        btn_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 4))
        ctk.CTkButton(btn_frame, text="💾 保存修改",
                      command=self._save_edit,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      height=32, corner_radius=6,
                      text_color="white", font=("", 12, "bold")
                      ).pack(side="left")
        ctk.CTkButton(btn_frame, text="🗑 删除",
                      command=self._confirm_delete,
                      fg_color="transparent", text_color="#b85450",
                      hover_color="#ffebee", height=32, corner_radius=6,
                      border_width=1, border_color="#b85450",
                      font=("", 12)
                      ).pack(side="right")

        ctk.CTkLabel(self.detail_frame,
                     text=f"📅 {rec.get('created_at_str', '')}",
                     font=("", 11), text_color=MUTED
                     ).pack(anchor="w", pady=(4, 0))

    def _save_edit(self):
        if not self.selected_id:
            return
        ta = self.ta_e.get("1.0", "end").strip()
        sup = self.sup_e.get("1.0", "end").strip()
        update_qa(self.selected_id, ta_answer=ta, teacher_supplement=sup)
        messagebox.showinfo("", "✅ 已保存")
        self._do_search()

    def _confirm_delete(self):
        if messagebox.askyesno("确认删除", "确定删除这条问答？"):
            delete_qa(self.selected_id)
            self.selected_id = None
            for w in self.detail_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(self.detail_frame, "已删除",
                         font=("", 13), text_color=MUTED).pack(pady=40)
            self._do_search()

    def _show_add_dialog(self):
        d = ctk.CTkToplevel(self.root)
        d.title("＋ 新增问答")
        d.geometry("500x480")
        d.configure(fg_color=BG)
        d.transient(self.root)
        d.grab_set()

        pad = 16
        ctk.CTkLabel(d, text="📝 新增问答",
                     font=FONT_TITLE, text_color=ACCENT
                     ).pack(padx=pad, pady=(14, 8), anchor="w")

        ctk.CTkLabel(d, text="问题 *", font=FONT_BODY
                     ).pack(padx=pad, anchor="w")
        qe = ctk.CTkTextbox(d, font=FONT_BODY, height=50,
                            fg_color=WHITE, border_width=1,
                            border_color=CARD_BORDER, corner_radius=6)
        qe.pack(padx=pad, fill="x", pady=2)

        ctk.CTkLabel(d, text="提问人（可选）", font=FONT_BODY
                     ).pack(padx=pad, anchor="w", pady=(6, 0))
        ae = ctk.CTkEntry(d, font=FONT_BODY, height=32,
                          fg_color=WHITE, border_width=1,
                          border_color=CARD_BORDER, corner_radius=6)
        ae.pack(padx=pad, fill="x", pady=2)

        ctk.CTkLabel(d, text="标签（逗号分隔，如: Python,安装）", font=FONT_BODY
                     ).pack(padx=pad, anchor="w", pady=(6, 0))
        te = ctk.CTkEntry(d, font=FONT_BODY, height=32,
                          fg_color=WHITE, border_width=1,
                          border_color=CARD_BORDER, corner_radius=6)
        te.pack(padx=pad, fill="x", pady=2)

        ctk.CTkLabel(d, text="助教回答（可选）", font=FONT_BODY
                     ).pack(padx=pad, anchor="w", pady=(6, 0))
        tae = ctk.CTkTextbox(d, font=FONT_BODY, height=60,
                             fg_color=WHITE, border_width=1,
                             border_color=CARD_BORDER, corner_radius=6)
        tae.pack(padx=pad, fill="x", pady=2)

        ctk.CTkLabel(d, text="我的补充（可选）", font=FONT_BODY
                     ).pack(padx=pad, anchor="w", pady=(6, 0))
        se = ctk.CTkTextbox(d, font=FONT_BODY, height=60,
                            fg_color=WHITE, border_width=1,
                            border_color=CARD_BORDER, corner_radius=6)
        se.pack(padx=pad, fill="x", pady=2)

        def save():
            q = qe.get("1.0", "end").strip()
            if not q:
                messagebox.showwarning("", "请填写问题", parent=d)
                return
            add_qa(q, tae.get("1.0", "end").strip(),
                   se.get("1.0", "end").strip(),
                   te.get().strip(), ae.get().strip())
            d.destroy()
            self._do_search()

        ctk.CTkFrame(d, fg_color="transparent"
                     ).pack(padx=pad, pady=(10, 16), fill="x")
        ctk.CTkButton(d, text="✅ 保存", command=save,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      height=36, corner_radius=8,
                      text_color="white", font=("", 13, "bold")
                      ).pack(padx=pad, pady=(0, 16), fill="x")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = QAKB()
    app.run()
