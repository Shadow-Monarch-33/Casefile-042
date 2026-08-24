import customtkinter as ctk
from database import get_connection

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CaseFileApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CASEFILE")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.create_layout()

        self.show_page("case overview")

    def create_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#0B1F3A"
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="CASEFILE",
            font=("Arial", 28, "bold"),
            text_color="#FFFFFF"
        )

        self.logo_label.pack(
            pady=(40, 5)
        )


        # Case number
        self.case_label = ctk.CTkLabel(
            self.sidebar,
            text="CASE #042",
            font=("Arial", 13),
            text_color="#7FA9D8"
        )

        self.case_label.pack(
            pady=(0, 30)
        )

        # Navigation buttons
        self.overview_button = ctk.CTkButton(
            self.sidebar,
            text="◉  Case Overview",
            font=("Arial", 15),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#16345C",
            command=lambda: self.show_page("case overview")
        )

        self.overview_button.pack(
            fill="x",
            padx=15,
            pady=(0, 8)
        )


        self.suspects_button = ctk.CTkButton(
            self.sidebar,
            text="◉  Suspects",
            font=("Arial", 15),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#16345C",
            command=lambda: self.show_page("suspects")
        )

        self.suspects_button.pack(
            fill="x",
            padx=15,
            pady=8
        )


        self.evidence_button = ctk.CTkButton(
            self.sidebar,
            text="◉  Evidence",
            font=("Arial", 15),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#16345C",
            command=lambda: self.show_page("evidence")
        )

        self.evidence_button.pack(
            fill="x",
            padx=15,
            pady=8
        )


        self.timeline_button = ctk.CTkButton(
            self.sidebar,
            text="◉  Timeline",
            font=("Arial", 15),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#16345C",
            command=lambda: self.show_page("timeline")
        )

        self.timeline_button.pack(
            fill="x",
            padx=15,
            pady=8
        )

        # Main Area
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#101827"
        )

        self.main_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

    def show_page(self, page_name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if page_name == "case overview":
            self.create_overview_page()

        elif page_name == "suspects":
            self.create_suspects_page()

        elif page_name == "evidence":
            self.create_evidence_page()

        elif page_name == "timeline":
            self.create_timeline_page()

    def create_overview_page(self):
        # Page header
        header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(40, 10)
        )

        # Case number
        case_number = ctk.CTkLabel(
            header,
            text="CASE #042",
            font=("Arial", 14, "bold"),
            text_color="#7FA9D8"
        )

        case_number.pack(
            anchor="w"
        )

        # Case title
        title = ctk.CTkLabel(
            header,
            text="THE LAST ACCESS",
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )

        title.pack(
            anchor="w",
            pady=(5, 5)
        )

        # Subtitle
        subtitle = ctk.CTkLabel(
            header,
            text="Homicide investigation • Executive Floor",
            font=("Arial", 15),
            text_color="#8B9BB4"
        )

        subtitle.pack(
            anchor="w"
        )

        # Case summary
        summary_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        summary_frame.pack(
            fill="x",
            padx=40,
            pady=(20, 15)
        )

        summary_title = ctk.CTkLabel(
            summary_frame,
            text="CASE SUMMARY",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        summary_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        summary_text = ctk.CTkLabel(
            summary_frame,
            text=(
                "At 11:05 PM, the victim was found dead inside his office on "
                "the executive floor. Multiple employees have been connected to "
                "suspicious activity during the estimated time of death."
            ),
            font=("Arial", 15),
            text_color="#D5DCE8",
            justify="left",
            wraplength=800
        )

        summary_text.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        # Statistics section
        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        stats_frame.pack(
            fill="x",
            padx=40,
            pady=(5, 20)
        )

        stats = [
            ("4", "SUSPECTS"),
            ("8", "EVIDENCE ITEMS"),
            ("9", "TIMELINE EVENTS"),
            ("2", "CRITICAL LEADS")
        ]

        for number, label in stats:

            card = ctk.CTkFrame(
                stats_frame,
                fg_color="#162235",
                corner_radius=12
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=6
            )

            number_label = ctk.CTkLabel(
                card,
                text=number,
                font=("Arial", 28, "bold"),
                text_color="#FFFFFF"
            )

            number_label.pack(
                pady=(18, 2)
            )

            text_label = ctk.CTkLabel(
                card,
                text=label,
                font=("Arial", 11, "bold"),
                text_color="#7D8DA6"
            )

            text_label.pack(
                pady=(0, 18)
            )

        # Key leads section
        leads_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        leads_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(0, 30)
        )

        leads_title = ctk.CTkLabel(
            leads_frame,
            text="KEY LEADS",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        leads_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        leads = [
            "CCTV footage was manually overridden between 10:10 PM and 10:28 PM.",
            "Elena's access card was used on the executive floor at 10:12 PM.",
            "Marcus's investor meeting ended earlier than he claimed.",
            "Sophie's lipstick was found inside the victim's office."
        ]

        for lead in leads:
            lead_label = ctk.CTkLabel(
                leads_frame,
                text="•  " + lead,
                font=("Arial", 14),
                text_color="#D5DCE8",
                justify="left",
                wraplength=800
            )

            lead_label.pack(
                anchor="w",
                padx=20,
                pady=5
            )

    def create_suspects_page(self):

        title = ctk.CTkLabel(
            self.main_frame,
            text="Suspects",
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )

        title.pack(
            anchor="w",
            padx=40,
            pady=(40, 5)
        )

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Individuals connected to CASE #042",
            font=("Arial", 14),
            text_color="#7D8DA6"
        )

        subtitle.pack(
            anchor="w",
            padx=40,
            pady=(0, 25)
        )

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM suspects")

        suspects = cursor.fetchall()

        cursor.close()
        connection.close()

        for suspect in suspects:
            print(suspect)

    def create_evidence_page(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Evidence",
            font=("Arial", 32, "bold")
        )

        title.pack(
            anchor="w",
            padx=40,
            pady=40
        )

    def create_timeline_page(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Timeline",
            font=("Arial", 32, "bold")
        )

        title.pack(
            anchor="w",
            padx=40,
            pady=40
        )

if __name__ == "__main__":
    app = CaseFileApp()
    app.mainloop()