import customtkinter as ctk

from properties import COLOR

class Notification(ctk.CTkFrame):
    def __init__(self, master, message: str, duration_sec: float, position: str = 'center'):
        super().__init__(master, fg_color=COLOR.NOTIFICATION_BACKGROUND,
                        corner_radius=0, border_color=COLOR.NOTIFICATION_OUTLINE,
                        border_width=3, width=1, height=1)
        self.message: str = message
        self.duration: int = int(duration_sec * 1000)
        self.position: str = position
        self.show_notification()

    def show_notification(self) -> None:
        self.text_label = ctk.CTkLabel(self, text=self.message, text_color=COLOR.TEXT, 
                                        font=ctk.CTkFont('Tiny5', size=32), anchor=ctk.N)
        self.text_label.pack(padx=10, pady=10)
        if self.position == 'center':
            self.place(relx=0.5, rely=0.47, anchor=ctk.CENTER)
        elif self.position == 'top':
            self.place(relx=0.5, y=20, anchor=ctk.N)
        self.master.after(self.duration, self.hide_notification)

    def hide_notification(self) -> None:
        self.destroy()
