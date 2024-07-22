import customtkinter as ctk
import pywinstyles

from properties import COLOR

class Notification(ctk.CTkFrame):
    def __init__(self, master, message: str, duration_sec: int):
        super().__init__(master, fg_color=COLOR.NOTIFICATION_BACKGROUND,
                        corner_radius=0, border_color=COLOR.NOTIFICATION_OUTLINE,
                        border_width=3)
        self.message = message
        self.duration = duration_sec * 1000
        self.show_notification()
        self.make_transparent()

    def make_transparent(self) -> None:
        pywinstyles.set_opacity(self.text_label, color='#000001')
        pywinstyles.set_opacity(self, color='#000001')

    def show_notification(self) -> None:
        self.text_label = ctk.CTkLabel(self, text=self.message, text_color=COLOR.TEXT, 
                                        font=ctk.CTkFont('Tiny5', size=32))
        self.text_label.pack(padx=10, pady=10)
        self.place(relx=0.5, rely=0.1, anchor=ctk.N)
        self.master.after(self.duration, self.hide_notification)

    def hide_notification(self) -> None:
        self.destroy()
