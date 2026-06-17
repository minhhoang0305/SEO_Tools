from __future__ import annotations

import asyncio
import json
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.platforms.api_client import ApiClientHelper


TENWORDS_API_URL = "https://app.10words.io/startups/"

CATEGORY_OPTIONS = {
    "Website": 1,
    "SaaS": 2,
    "Mobile App": 3,
    "Newsletter": 4,
    "Other": 5,
}


class TenWordsSubmitUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("10words API Submit")
        self.geometry("860x760")
        self.minsize(780, 680)
        self.result_queue: queue.Queue[tuple[str, object]] = queue.Queue()

        self._build_styles()
        self._build_layout()

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Title.TLabel", font=("Helvetica Neue", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Helvetica Neue", 11))
        style.configure("Section.TLabel", font=("Helvetica Neue", 12, "bold"))
        style.configure("Primary.TButton", font=("Helvetica Neue", 11, "bold"), padding=(14, 8))
        style.configure("TLabel", font=("Helvetica Neue", 10))
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=6)

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 18))

        ttk.Label(header, text="10words API Submit", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Nhập token và thông tin project, rồi submit thẳng vào https://app.10words.io/startups/",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        form = ttk.Frame(container)
        form.pack(fill="x")

        self.api_token_var = tk.StringVar()
        self.name_var = tk.StringVar(value="SEO TOOLS")
        self.link_var = tk.StringVar(value="https://example.com")
        self.twitter_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Website")
        self.newsletter_var = tk.BooleanVar(value=False)

        self._add_entry(form, "API Token", self.api_token_var, row=0, show="*")
        self._add_entry(form, "Name", self.name_var, row=1)
        self._add_entry(form, "Link", self.link_var, row=2)
        self._add_entry(form, "Twitter", self.twitter_var, row=3)

        ttk.Label(form, text="Description", style="Section.TLabel").grid(row=4, column=0, sticky="w", pady=(14, 6))
        self.description_text = ScrolledText(form, height=8, wrap="word", font=("Helvetica Neue", 10))
        self.description_text.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.description_text.insert("1.0", "My Project")

        ttk.Label(form, text="Category", style="Section.TLabel").grid(row=6, column=0, sticky="w", pady=(14, 6))
        category_frame = ttk.Frame(form)
        category_frame.grid(row=7, column=0, columnspan=3, sticky="ew")
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=list(CATEGORY_OPTIONS.keys()),
            state="readonly",
            width=22,
        )
        self.category_combo.pack(side="left", padx=(0, 16))

        self.category_id_var = tk.StringVar(value="1")
        ttk.Label(category_frame, text="Category ID").pack(side="left")
        ttk.Entry(category_frame, textvariable=self.category_id_var, width=10).pack(side="left", padx=(8, 0))
        ttk.Label(category_frame, text="(Website = 1)").pack(side="left", padx=(8, 0))

        newsletter_frame = ttk.Frame(form)
        newsletter_frame.grid(row=8, column=0, columnspan=3, sticky="w", pady=(14, 0))
        ttk.Checkbutton(
            newsletter_frame,
            text="Include newsletter",
            variable=self.newsletter_var,
        ).pack(side="left")
        ttk.Label(newsletter_frame, text="(unchecked = 0, checked = 1)").pack(side="left", padx=(8, 0))

        button_bar = ttk.Frame(container)
        button_bar.pack(fill="x", pady=(18, 12))

        ttk.Button(button_bar, text="Submit", style="Primary.TButton", command=self._submit_clicked).pack(side="left")
        ttk.Button(button_bar, text="Fill Sample", command=self._fill_sample).pack(side="left", padx=(10, 0))
        ttk.Button(button_bar, text="Clear", command=self._clear_form).pack(side="left", padx=(10, 0))

        ttk.Label(container, text="Output", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.output = ScrolledText(container, height=14, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)
        self._log("UI sẵn sàng. Nhập token rồi bấm Submit.")

    def _add_entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, show: str | None = None) -> None:
        ttk.Label(parent, text=label, style="Section.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 6))
        entry = ttk.Entry(parent, textvariable=variable, show=show or "")
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)

    def _fill_sample(self) -> None:
        self.api_token_var.set("")
        self.name_var.set("SEO TOOLS")
        self.link_var.set("https://example.com")
        self.twitter_var.set("")
        self.category_var.set("Website")
        self.category_id_var.set("1")
        self.newsletter_var.set(False)
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", "My Project")
        self._log("Đã điền dữ liệu mẫu.")

    def _clear_form(self) -> None:
        self.api_token_var.set("")
        self.name_var.set("")
        self.link_var.set("")
        self.twitter_var.set("")
        self.category_var.set("Website")
        self.category_id_var.set("1")
        self.newsletter_var.set(False)
        self.description_text.delete("1.0", "end")
        self.output.delete("1.0", "end")

    def _log(self, message: str) -> None:
        self.output.insert("end", f"{message}\n")
        self.output.see("end")

    def _set_busy(self, busy: bool) -> None:
        state_flag = ["disabled"] if busy else ["!disabled"]
        for child in self.winfo_children():
            self._set_widget_state_recursive(child, state_flag)
        self.update_idletasks()

    def _set_widget_state_recursive(self, widget, state_flag: list[str]) -> None:
        try:
            if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox, ttk.Checkbutton)):
                widget.state(state_flag) if hasattr(widget, "state") else None
        except Exception:
            pass
        for child in getattr(widget, "winfo_children", lambda: [])():
            self._set_widget_state_recursive(child, state_flag)

    def _build_payload(self) -> dict[str, object]:
        api_token = self.api_token_var.get().strip()
        project_name = self.name_var.get().strip()
        project_url = self.link_var.get().strip()
        twitter_handle = self.twitter_var.get().strip().lstrip("@")
        description = self.description_text.get("1.0", "end").strip()
        category_name = self.category_var.get().strip() or "Website"

        category_id = CATEGORY_OPTIONS.get(category_name, 1)
        try:
            category_id = int(self.category_id_var.get().strip())
        except Exception:
            pass

        return {
            "api_token": api_token,
            "payload": {
                "name": project_name,
                "description": description,
                "link": project_url,
                "twitter": twitter_handle,
                "category": category_id,
                "newsletter": 1 if self.newsletter_var.get() else 0,
            },
        }

    def _submit_clicked(self) -> None:
        data = self._build_payload()
        api_token = str(data["api_token"]).strip()
        payload = data["payload"]

        if not api_token:
            messagebox.showerror("Thiếu token", "Bạn cần nhập API token của 10words.")
            return

        if not payload["name"] or not payload["link"] or not payload["description"]:
            messagebox.showerror("Thiếu dữ liệu", "Name, Description và Link là bắt buộc.")
            return

        self._set_busy(True)
        self._log("Đang submit tới 10words API...")
        threading.Thread(
            target=self._submit_worker,
            args=(api_token, payload),
            daemon=True,
        ).start()
        self.after(150, self._poll_result_queue)

    def _submit_worker(self, api_token: str, payload: dict[str, object]) -> None:
        asyncio.run(self._submit_async(api_token, payload))

    async def _submit_async(self, api_token: str, payload: dict[str, object]) -> None:
        headers = {
            "Authorization": f"Token {api_token}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://portal.10words.io",
            "Referer": "https://portal.10words.io/",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
            ),
        }

        client = ApiClientHelper(timeout=20.0, follow_redirects=True)
        try:
            response = await client.post(TENWORDS_API_URL, headers=headers, json=payload)
            self.result_queue.put(("result", (response.status_code, response.json_data or response.text)))
        except Exception as exc:
            self.result_queue.put(("error", str(exc)))

    def _poll_result_queue(self) -> None:
        try:
            kind, payload = self.result_queue.get_nowait()
        except queue.Empty:
            self.after(150, self._poll_result_queue)
            return

        self._set_busy(False)
        if kind == "result":
            status_code, result = payload  # type: ignore[misc]
            pretty = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
            self._log(f"HTTP {status_code}")
            self._log(pretty)
            if status_code in {200, 201}:
                messagebox.showinfo("Thành công", "Submit 10words API đã hoàn tất.")
            else:
                messagebox.showwarning("Chưa thành công", f"API trả về HTTP {status_code}.")
        else:
            error_message = str(payload)
            self._log(f"Lỗi: {error_message}")
            messagebox.showerror("Lỗi submit", error_message)


def main() -> None:
    app = TenWordsSubmitUI()
    app.mainloop()


if __name__ == "__main__":
    main()
