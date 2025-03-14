"""File containing implementation for in app notifications.
"""

import customtkinter as ctk
from typing import Any
import platform
if platform.system() == 'Windows':
    import pywinstyles

from tools import get_from_config
from properties import COLOR

class Notification(ctk.CTkFrame):
    """Class handling showing notifications in the app.

    Args:

     - ctk.CTkFrame : Inheritance from customtkinter CTkFrame widget. 
    """
    def __init__(self, master: Any, message: str, duration_sec: float, position: str='center'):
        """Constructor:

         - loads font name from config
         - converts amount of seconds to milliseconds
         - shows itself at the end

        Args:

         - master (Any): Parent widget
         - message (str): Desired message to show on screen
         - duration_sec (float): Amount of seconds before hiding the notification.
         - position (str, optional): Position of the notification 'center' or 'top'. Defaults to 'center'.
        """
        super().__init__(master, fg_color=COLOR.NOTIFICATION_BACKGROUND,
                        corner_radius=0, border_color=COLOR.NOTIFICATION_OUTLINE,
                        border_width=3, width=1, height=1)
        self.font_name: str = str(get_from_config('font_name'))
        self.message: str = message
        self.duration: int = int(duration_sec * 1000)
        self.position: str = position
        self.show_notification()

    def show_notification(self) -> None:
        """Places the notification on top of all widgets relatively to the window size.
        """
        self.text_label = ctk.CTkLabel(self, text=self.message, text_color=COLOR.TEXT, 
                                        font=ctk.CTkFont(self.font_name, size=32), anchor=ctk.N)
        self.text_label.pack(padx=10, pady=10)
        if self.position == 'center':
            self.place(relx=0.504, rely=0.47, anchor=ctk.CENTER)
        elif self.position == 'top':
            self.place(relx=0.5, y=20, anchor=ctk.N)
        self.show_animation(0)

    def show_animation(self, i: int) -> None:
        """Animates the notification appearing on the screen. At the end calls hide_notification delayed by (duration_sec * 1000).

        Args:

         - i (int): Iteration value passed by recursive formula.
        """
        if not self.winfo_exists:
            return
        if i < 100:
            i += 1
            if platform.system() == 'Windows':
                pywinstyles.set_opacity(self, value=(0.01*i), color='#000001')
            self.master.after(1, lambda: self.show_animation(i))
        else:
            self.master.after(self.duration, lambda: self.hide_notification(0))

    def hide_notification(self, i: int) -> None:
        """Animates the notification before removing it from the screen.

        Args:

         - i (int): Iteration value passed by recursive formula.
        """
        if i < 100:
            i += 1
            if self.winfo_exists():
                if platform.system() == 'Windows':
                    pywinstyles.set_opacity(self, value=(1 - (0.01*i)), color='#000001')
                self.master.after(1, lambda: self.hide_notification(i))
        else:
            self.destroy()
