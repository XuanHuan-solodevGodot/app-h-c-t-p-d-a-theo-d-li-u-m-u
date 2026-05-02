"""
==============================================================
  ỨNG DỤNG ÔN TẬP TRẮC NGHIỆM - Phiên bản Tkinter
  Tác giả: Python Expert Assistant
  Mô tả: Chương trình ôn tập trắc nghiệm với giao diện đồ họa
==============================================================
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random
import re

# ─────────────────────────────────────────────
#  CÁC HẰNG SỐ MÀU SẮC VÀ FONT CHỮ
# ─────────────────────────────────────────────
# Màu nền và chữ chính
BG_APP          = "#1E1E2E"   # Nền ứng dụng – xanh đêm sâu
BG_HEADER       = "#2A2A3E"   # Nền thanh tiêu đề
BG_CARD         = "#2E2E42"   # Nền thẻ câu hỏi
BG_BTN_OPTION   = "#3A3A54"   # Nền nút phương án (mặc định)
BG_BTN_ACTION   = "#5C6BC0"   # Nền nút hành động (Tiếp theo, Xáo trộn)
BG_BTN_FILE     = "#37474F"   # Nền nút chọn file

FG_MAIN         = "#E8EAF6"   # Màu chữ chính – trắng sáng
FG_SUBTITLE     = "#9FA8DA"   # Màu chữ phụ – tím nhạt
FG_CORRECT      = "#FFFFFF"   # Chữ khi đúng
FG_WRONG        = "#FFFFFF"   # Chữ khi sai

COLOR_CORRECT   = "#2E7D32"   # Xanh lá khi đúng
COLOR_WRONG     = "#C62828"   # Đỏ khi sai
COLOR_HOVER     = "#4A4A6A"   # Màu hover nút phương án
COLOR_NEXT_HOVER = "#3949AB"  # Màu hover nút Tiếp theo

FONT_TITLE      = ("Segoe UI", 16, "bold")
FONT_COUNTER    = ("Segoe UI", 11)
FONT_QUESTION   = ("Segoe UI", 13)
FONT_OPTION     = ("Segoe UI", 12)
FONT_BTN_ACTION = ("Segoe UI", 11, "bold")
FONT_FEEDBACK   = ("Segoe UI", 12, "bold")
FONT_SCORE      = ("Segoe UI", 11)


# ─────────────────────────────────────────────
#  LỚP ĐỌC VÀ PHÂN TÍCH FILE DỮ LIỆU
# ─────────────────────────────────────────────
class QuizParser:
    """
    Chịu trách nhiệm đọc file văn bản và phân tích
    thành danh sách các câu hỏi có cấu trúc.
    """

    @staticmethod
    def parse(filepath: str) -> list[dict]:
        """
        Đọc file và trả về danh sách dict, mỗi dict gồm:
          - 'question' : str  – nội dung câu hỏi
          - 'options'  : list – danh sách ['A. ...', 'B. ...', ...]
          - 'answer'   : str  – đáp án đúng (ví dụ 'A. O(n)')
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        questions = []
        # Tách các khối câu hỏi dựa trên dòng trống
        # Mỗi câu hỏi bắt đầu bằng số thứ tự (1. 2. 10. ...)
        blocks = re.split(r'\n{2,}', content.strip())

        for block in blocks:
            lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
            if not lines:
                continue

            q_text    = ""
            options   = []
            answer    = ""

            for line in lines:
                # Dòng câu hỏi: bắt đầu bằng số + dấu chấm
                if re.match(r'^\d+\.', line):
                    # Bỏ số thứ tự đầu dòng
                    q_text = re.sub(r'^\d+\.\s*', '', line).strip()

                # Dòng phương án: A. / B. / C. / D.
                elif re.match(r'^[A-D]\.', line):
                    options.append(line)

                # Dòng đáp án
                elif line.lower().startswith("đáp án đúng"):
                    # Lấy phần sau dấu ':' và bỏ khoảng trắng
                    answer = line.split(":", 1)[-1].strip()

            # Chỉ thêm vào danh sách khi đủ dữ liệu hợp lệ
            if q_text and len(options) >= 2 and answer:
                questions.append({
                    "question": q_text,
                    "options" : options,
                    "answer"  : answer,
                })

        return questions


# ─────────────────────────────────────────────
#  LỚP CHÍNH – ỨNG DỤNG TKINTER
# ─────────────────────────────────────────────
class QuizApp(tk.Tk):
    """
    Lớp chính quản lý toàn bộ giao diện và logic
    của ứng dụng ôn tập trắc nghiệm.
    """

    def __init__(self):
        super().__init__()

        # ── Cấu hình cửa sổ chính ──
        self.title("📚 Ôn Tập Trắc Nghiệm")
        self.geometry("780x620")
        self.minsize(680, 540)
        self.configure(bg=BG_APP)
        self.resizable(True, True)

        # ── Trạng thái ứng dụng ──
        self.questions       : list[dict] = []   # Danh sách câu hỏi
        self.current_index   : int        = 0    # Chỉ số câu hiện tại
        self.score           : int        = 0    # Điểm số (số câu trả lời đúng lần đầu)
        self.answered_correct: bool       = False # Đã trả lời đúng câu hiện tại chưa?
        self.option_buttons  : list       = []   # Danh sách các nút phương án

        # ── Xây dựng giao diện ──
        self._build_ui()

    # ══════════════════════════════════════════
    #  XÂY DỰNG GIAO DIỆN (UI)
    # ══════════════════════════════════════════

    def _build_ui(self):
        """Khởi tạo và sắp xếp tất cả các widget."""

        # ── THANH TIÊU ĐỀ ──
        header = tk.Frame(self, bg=BG_HEADER, pady=12)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="📚  ÔN TẬP TRẮC NGHIỆM",
            font=FONT_TITLE,
            bg=BG_HEADER,
            fg=FG_MAIN,
        ).pack(side=tk.LEFT, padx=20)

        # Nút chọn file trong thanh tiêu đề
        self._btn_new_file = self._make_btn(
            header, "📂  Chọn File Mới",
            self._open_file, BG_BTN_FILE, side=tk.RIGHT, padx=(0, 10)
        )

        # ── KHU VỰC NỘI DUNG CHÍNH (cuộn được) ──
        self.main_frame = tk.Frame(self, bg=BG_APP)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(14, 0))

        # ── MÀN HÌNH CHÀO MỪNG (hiển thị khi chưa có file) ──
        self._build_welcome_screen()

        # ── MÀN HÌNH CÂU HỎI (ẩn cho đến khi load file) ──
        self._build_quiz_screen()

        # Mặc định chỉ hiện màn hình chào
        self.quiz_frame.pack_forget()

        # ── THANH TRẠNG THÁI DƯỚI CÙNG ──
        self._build_status_bar()

    # ── Màn hình chào mừng ──────────────────
    def _build_welcome_screen(self):
        """Giao diện hiển thị khi chưa tải file câu hỏi."""
        self.welcome_frame = tk.Frame(self.main_frame, bg=BG_APP)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

        # Căn giữa theo chiều dọc
        spacer = tk.Frame(self.welcome_frame, bg=BG_APP)
        spacer.pack(expand=True)

        tk.Label(
            spacer, text="📂", font=("Segoe UI", 52),
            bg=BG_APP, fg=FG_SUBTITLE
        ).pack(pady=(0, 8))

        tk.Label(
            spacer,
            text="Chưa có dữ liệu câu hỏi",
            font=("Segoe UI", 17, "bold"),
            bg=BG_APP, fg=FG_MAIN,
        ).pack()

        tk.Label(
            spacer,
            text="Nhấn nút bên dưới để mở file câu hỏi (.txt)\nđịnh dạng theo hướng dẫn và bắt đầu ôn tập.",
            font=("Segoe UI", 11),
            bg=BG_APP, fg=FG_SUBTITLE,
            justify=tk.CENTER,
        ).pack(pady=(6, 20))

        self._make_btn(
            spacer, "📂   Chọn File Câu Hỏi",
            self._open_file, BG_BTN_ACTION,
            font=FONT_BTN_ACTION, padx=0, pady=4
        )

        tk.Frame(self.welcome_frame, bg=BG_APP).pack(expand=True)

    # ── Màn hình câu hỏi ────────────────────
    def _build_quiz_screen(self):
        """Giao diện hiển thị khi đang làm bài."""
        self.quiz_frame = tk.Frame(self.main_frame, bg=BG_APP)

        # Bộ đếm câu + điểm
        top_row = tk.Frame(self.quiz_frame, bg=BG_APP)
        top_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_counter = tk.Label(
            top_row, text="Câu 0 / 0",
            font=FONT_COUNTER, bg=BG_APP, fg=FG_SUBTITLE,
        )
        self.lbl_counter.pack(side=tk.LEFT)

        self.lbl_score = tk.Label(
            top_row, text="⭐ Điểm: 0",
            font=FONT_SCORE, bg=BG_APP, fg=FG_SUBTITLE,
        )
        self.lbl_score.pack(side=tk.RIGHT)

        # Thanh tiến trình
        self.progress_canvas = tk.Canvas(
            self.quiz_frame, height=6, bg="#3A3A54",
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=(0, 14))

        # Thẻ câu hỏi
        q_card = tk.Frame(
            self.quiz_frame, bg=BG_CARD,
            padx=20, pady=16,
        )
        q_card.pack(fill=tk.X, pady=(0, 14))

        self.lbl_question = tk.Label(
            q_card,
            text="",
            font=FONT_QUESTION,
            bg=BG_CARD, fg=FG_MAIN,
            wraplength=680,
            justify=tk.LEFT,
            anchor="w",
        )
        self.lbl_question.pack(fill=tk.X)

        # Khung chứa các nút phương án
        self.options_frame = tk.Frame(self.quiz_frame, bg=BG_APP)
        self.options_frame.pack(fill=tk.X, pady=(0, 10))

        # Nhãn phản hồi đúng/sai
        self.lbl_feedback = tk.Label(
            self.quiz_frame, text="",
            font=FONT_FEEDBACK, bg=BG_APP, fg=FG_MAIN,
        )
        self.lbl_feedback.pack(pady=(0, 6))

        # Hàng nút hành động
        action_row = tk.Frame(self.quiz_frame, bg=BG_APP)
        action_row.pack(pady=(4, 8))

        self._btn_next = self._make_btn(
            action_row, "Câu tiếp theo  ➜",
            self._next_question, BG_BTN_ACTION,
            state=tk.DISABLED, side=tk.LEFT, padx=(0, 8),
        )

        self._btn_shuffle = self._make_btn(
            action_row, "🔀  Xáo trộn & Tua lại",
            self._shuffle_and_restart, "#546E7A",
            side=tk.LEFT,
        )

    # ── Thanh trạng thái dưới cùng ──────────
    def _build_status_bar(self):
        """Thanh thông tin nhỏ ở đáy cửa sổ."""
        bar = tk.Frame(self, bg=BG_HEADER, pady=5)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.lbl_status = tk.Label(
            bar, text="Chưa tải file.",
            font=("Segoe UI", 9),
            bg=BG_HEADER, fg=FG_SUBTITLE,
        )
        self.lbl_status.pack()

    # ══════════════════════════════════════════
    #  HELPER: TẠO NÚT BẤM THỐNG NHẤT
    # ══════════════════════════════════════════

    def _make_btn(
        self, parent, text, command,
        bg=BG_BTN_ACTION, fg=FG_MAIN,
        font=None, state=tk.NORMAL,
        side=None, padx=0, pady=0, **kw
    ):
        """
        Tạo một nút bấm với phong cách thống nhất,
        có hiệu ứng hover nhẹ.
        """
        if font is None:
            font = FONT_BTN_ACTION

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            bg=bg, fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=tk.FLAT,
            cursor="hand2",
            state=state,
            padx=14, pady=7,
            bd=0,
            **kw
        )

        if side is not None:
            btn.pack(side=side, padx=padx, pady=pady)
        else:
            btn.pack(padx=padx, pady=pady)

        # Hiệu ứng hover
        original_bg = bg
        def on_enter(e): btn.config(bg=self._lighten(original_bg))
        def on_leave(e): btn.config(bg=original_bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    @staticmethod
    def _lighten(hex_color: str, amount: int = 20) -> str:
        """Làm sáng màu hex một chút cho hiệu ứng hover."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [min(255, int(hex_color[i:i+2], 16) + amount) for i in (0, 2, 4)]
        return f"#{r:02X}{g:02X}{b:02X}"

    # ══════════════════════════════════════════
    #  XỬ LÝ FILE
    # ══════════════════════════════════════════

    def _open_file(self):
        """Mở hộp thoại chọn file và tải dữ liệu câu hỏi."""
        filepath = filedialog.askopenfilename(
            title="Chọn file câu hỏi",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not filepath:
            return  # Người dùng hủy

        try:
            questions = QuizParser.parse(filepath)
        except Exception as err:
            messagebox.showerror("Lỗi đọc file", f"Không thể đọc file:\n{err}")
            return

        if not questions:
            messagebox.showwarning(
                "Không tìm thấy câu hỏi",
                "File không chứa câu hỏi hợp lệ.\n"
                "Vui lòng kiểm tra lại định dạng file.",
            )
            return

        # Tải thành công → khởi động quiz
        self.questions = questions
        self._start_quiz()

        # Cập nhật thanh trạng thái
        import os
        fname = os.path.basename(filepath)
        self.lbl_status.config(
            text=f"✅  Đã tải: {fname}  —  {len(questions)} câu hỏi"
        )

    # ══════════════════════════════════════════
    #  KHỞI ĐỘNG & ĐIỀU HƯỚNG QUIZ
    # ══════════════════════════════════════════

    def _start_quiz(self):
        """Reset trạng thái và bắt đầu từ câu đầu tiên."""
        self.current_index    = 0
        self.score            = 0
        self.answered_correct = False

        # Chuyển từ màn hình chào → màn hình quiz
        self.welcome_frame.pack_forget()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)

        self._show_question()

    def _show_question(self):
        """Hiển thị câu hỏi tại chỉ số hiện tại."""
        if self.current_index >= len(self.questions):
            self._show_finish_screen()
            return

        q = self.questions[self.current_index]
        total = len(self.questions)
        idx   = self.current_index + 1

        # Cập nhật bộ đếm & điểm
        self.lbl_counter.config(text=f"Câu {idx} / {total}")
        self.lbl_score.config(text=f"⭐ Điểm: {self.score}")

        # Cập nhật thanh tiến trình
        self._update_progress(idx, total)

        # Nội dung câu hỏi
        self.lbl_question.config(text=q["question"])

        # Xóa phản hồi cũ
        self.lbl_feedback.config(text="")

        # Reset cờ trả lời
        self.answered_correct = False

        # Tắt nút "Tiếp theo" cho đến khi trả lời đúng
        self._btn_next.config(state=tk.DISABLED)

        # Vẽ lại các nút phương án
        self._render_options(q["options"], q["answer"])

    def _render_options(self, options: list[str], correct_answer: str):
        """Xóa các nút cũ và tạo mới các nút phương án."""
        # Hủy tất cả widget con cũ
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_buttons.clear()

        for opt in options:
            btn = tk.Button(
                self.options_frame,
                text=opt,
                font=FONT_OPTION,
                bg=BG_BTN_OPTION,
                fg=FG_MAIN,
                activebackground=COLOR_HOVER,
                activeforeground=FG_MAIN,
                relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                padx=16, pady=9,
                bd=0,
                wraplength=660,
                justify=tk.LEFT,
            )
            btn.pack(fill=tk.X, pady=4)

            # Gắn sự kiện click với đáp án tương ứng
            btn.config(
                command=lambda b=btn, o=opt, ca=correct_answer:
                    self._check_answer(b, o, ca)
            )

            # Hover effect
            def on_enter(e, b=btn): b.config(bg=COLOR_HOVER)
            def on_leave(e, b=btn): b.config(bg=BG_BTN_OPTION)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            self.option_buttons.append(btn)

    def _check_answer(self, clicked_btn: tk.Button, chosen: str, correct: str):
        """
        Kiểm tra đáp án người dùng chọn.
        Đúng  → tô xanh, thông báo, mở nút Tiếp theo.
        Sai   → tô đỏ, thông báo, cho chọn lại.
        """
        # Tắt tất cả nút (tránh spam click)
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)

        # So sánh phương án đã chọn với đáp án đúng
        # (so sánh linh hoạt: lấy chữ cái đầu hoặc toàn chuỗi)
        is_correct = self._compare_answer(chosen, correct)

        if is_correct:
            # Đúng
            clicked_btn.config(bg=COLOR_CORRECT, fg=FG_CORRECT)
            self.lbl_feedback.config(text="✅  Chính xác!", fg="#66BB6A")
            self._btn_next.config(state=tk.NORMAL)

            # Cộng điểm nếu đây là lần đầu trả lời đúng câu này
            if not self.answered_correct:
                self.score += 1
                self.answered_correct = True
        else:
            # Sai
            clicked_btn.config(bg=COLOR_WRONG, fg=FG_WRONG)
            self.lbl_feedback.config(
                text="❌  Sai rồi, hãy chọn lại!", fg="#EF5350"
            )
            # Kích hoạt lại các nút chưa bị chọn sai
            self.after(700, lambda: self._re_enable_options(clicked_btn))

    def _re_enable_options(self, wrong_btn: tk.Button):
        """
        Kích hoạt lại tất cả nút phương án trừ nút vừa chọn sai,
        để người dùng tiếp tục chọn lại.
        """
        for btn in self.option_buttons:
            if btn is not wrong_btn:
                btn.config(state=tk.NORMAL)
        # Giữ màu đỏ ở nút sai; các nút khác trở về màu gốc
        wrong_btn.config(state=tk.DISABLED, bg=COLOR_WRONG)

    @staticmethod
    def _compare_answer(chosen: str, correct: str) -> bool:
        """
        So sánh linh hoạt: chỉ cần ký tự đầu (A/B/C/D) khớp là được.
        Ví dụ: 'A. O(n)' == 'A. O(n)' hoặc chỉ cần 'A' == 'A'.
        """
        # Chuẩn hóa: lấy ký tự đầu tiên (A/B/C/D)
        def first_letter(s: str) -> str:
            s = s.strip()
            return s[0].upper() if s else ""

        # Nếu đáp án đúng trong file có thể là 'A. O(n)' hoặc 'A'
        # Ta so sánh full string trước, fallback sang ký tự đầu
        if chosen.strip() == correct.strip():
            return True
        return first_letter(chosen) == first_letter(correct)

    def _next_question(self):
        """Chuyển sang câu hỏi tiếp theo."""
        self.current_index += 1
        self._btn_next.config(state=tk.DISABLED)
        self._show_question()

    # ══════════════════════════════════════════
    #  CHỨC NĂNG NÂNG CAO
    # ══════════════════════════════════════════

    def _shuffle_and_restart(self):
        """Xáo trộn ngẫu nhiên danh sách câu hỏi và bắt đầu lại."""
        if not self.questions:
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu câu hỏi.")
            return

        confirm = messagebox.askyesno(
            "Xáo trộn & Tua lại",
            "Bạn có muốn xáo trộn câu hỏi và bắt đầu lại từ đầu không?\n"
            "Điểm hiện tại sẽ được reset.",
        )
        if confirm:
            random.shuffle(self.questions)
            self._start_quiz()

    # ══════════════════════════════════════════
    #  THANH TIẾN TRÌNH
    # ══════════════════════════════════════════

    def _update_progress(self, current: int, total: int):
        """Cập nhật thanh tiến trình dạng canvas."""
        self.progress_canvas.update_idletasks()
        width = self.progress_canvas.winfo_width()
        if width <= 1:
            width = 740  # fallback

        fill_width = int(width * current / total)

        self.progress_canvas.delete("all")
        # Nền
        self.progress_canvas.create_rectangle(
            0, 0, width, 6, fill="#3A3A54", outline=""
        )
        # Phần đã hoàn thành
        if fill_width > 0:
            self.progress_canvas.create_rectangle(
                0, 0, fill_width, 6, fill="#5C6BC0", outline=""
            )

    # ══════════════════════════════════════════
    #  MÀN HÌNH KẾT THÚC
    # ══════════════════════════════════════════

    def _show_finish_screen(self):
        """Hiển thị kết quả khi đã trả lời hết câu hỏi."""
        total = len(self.questions)
        pct   = round(self.score / total * 100) if total else 0

        # Xóa nội dung quiz cũ
        self.quiz_frame.pack_forget()

        # Tạo khung kết quả tạm thời
        finish = tk.Frame(self.main_frame, bg=BG_APP)
        finish.pack(fill=tk.BOTH, expand=True)
        self._finish_frame = finish  # lưu để xóa sau

        spacer = tk.Frame(finish, bg=BG_APP)
        spacer.pack(expand=True)

        emoji = "🏆" if pct >= 80 else "📝" if pct >= 50 else "💪"
        tk.Label(spacer, text=emoji, font=("Segoe UI", 54),
                 bg=BG_APP, fg=FG_MAIN).pack(pady=(0, 8))

        tk.Label(
            spacer, text="Bạn đã hoàn thành bài!",
            font=("Segoe UI", 18, "bold"),
            bg=BG_APP, fg=FG_MAIN,
        ).pack()

        result_text = (
            f"Trả lời đúng ngay lần đầu: {self.score} / {total} câu\n"
            f"Tỉ lệ đúng: {pct}%"
        )
        tk.Label(
            spacer, text=result_text,
            font=("Segoe UI", 13),
            bg=BG_APP, fg=FG_SUBTITLE,
            justify=tk.CENTER,
        ).pack(pady=(8, 20))

        # Nút hành động
        btn_row = tk.Frame(spacer, bg=BG_APP)
        btn_row.pack()

        self._make_btn(
            btn_row, "🔀  Xáo trộn & Làm lại",
            self._retry_shuffled, BG_BTN_ACTION,
            side=tk.LEFT, padx=(0, 10)
        )
        self._make_btn(
            btn_row, "📂  Chọn File Mới",
            self._reset_to_welcome, BG_BTN_FILE,
            side=tk.LEFT,
        )

        tk.Frame(finish, bg=BG_APP).pack(expand=True)

    def _retry_shuffled(self):
        """Xáo trộn và làm lại ngay từ màn hình kết quả."""
        if hasattr(self, "_finish_frame"):
            self._finish_frame.destroy()
        random.shuffle(self.questions)
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self._start_quiz()

    def _reset_to_welcome(self):
        """Xóa dữ liệu và quay về màn hình chào."""
        if hasattr(self, "_finish_frame"):
            self._finish_frame.destroy()
        self.questions = []
        self.quiz_frame.pack_forget()
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        self.lbl_status.config(text="Chưa tải file.")


# ─────────────────────────────────────────────
#  ĐIỂM VÀO CHƯƠNG TRÌNH
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
