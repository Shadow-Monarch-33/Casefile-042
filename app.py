import customtkinter as ctk
from database import get_connection

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CaseFileApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.investigated_evidence = set()
        self.discovered_leads = set()
        self.valid_connections = {
            frozenset({1, 4}): {
                "id": "access_during_blackout",
                "title": "ACCESS DURING BLACKOUT",
                "description": (
                    "The access card activity occurred while "
                    "the executive floor security cameras were offline."
                ),
                "evidence_ids": {1, 4}
            }
        }

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


        self.deduction_board_button = ctk.CTkButton(
            self.sidebar,
            text="◉  Deduction Board",
            font=("Arial", 15),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#16345C",
            command=lambda: self.show_page("deduction board")
        )

        self.deduction_board_button.pack(
            fill="x",
            padx=15,
            pady=8
        )

        # Main Area
        self.main_frame = ctk.CTkScrollableFrame(
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

        elif page_name == "deduction board":
            self.create_deduction_board_page()

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

        # Get statistics from database

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM suspects")
        suspect_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM evidence")
        evidence_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM timeline")
        timeline_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM evidence
            WHERE importance = 'Critical'
        """)
        critical_count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

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
            (str(suspect_count), "SUSPECTS"),
            (str(evidence_count), "EVIDENCE ITEMS"),
            (str(timeline_count), "TIMELINE EVENTS"),
            (str(critical_count), "CRITICAL LEADS")
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
            fill="x",
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
            card = ctk.CTkFrame(
                self.main_frame,
                fg_color="#162235",
                corner_radius=12
            )

            card.pack(
                fill="x",
                padx=40,
                pady=8
            )

            name_label = ctk.CTkLabel(
                card,
                text=suspect["name"],
                font=("Arial", 20, "bold"),
                text_color="#FFFFFF"
            )

            name_label.pack(
                anchor="w",
                padx=20,
                pady=(15, 2)
            )

            details_label = ctk.CTkLabel(
                card,
                text=f'{suspect["age"]} years old  •  {suspect["occupation"]}',
                font=("Arial", 13),
                text_color="#7D8DA6"
            )

            details_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 8)
            )

            status_label = ctk.CTkLabel(
                card,
                text=suspect["status"],
                font=("Arial", 12, "bold"),
                text_color="#7FA9D8"
            )

            status_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 15)
            )

            view_button = ctk.CTkButton(
                card,
                text="VIEW PROFILE  →",
                font=("Arial", 12, "bold"),
                width=140,
                height=32,
                fg_color="#1D4E89",
                hover_color="#2863A8",
                command=lambda suspect_id=suspect["id"]: self.show_suspect_details(suspect_id)
            )

            view_button.pack(
                anchor="e",
                padx=20,
                pady=(0, 15)
            )

    def show_suspect_details(self, suspect_id):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        back_button = ctk.CTkButton(
            self.main_frame,
            text="← BACK TO SUSPECTS",
            font=("Arial", 12, "bold"),
            width=170,
            height=35,
            fg_color="transparent",
            border_width=1,
            border_color="#2A3D57",
            hover_color="#1C2C44",
            command=lambda: self.show_page("suspects")
        )

        back_button.pack(
            anchor="w",
            padx=40,
            pady=(30, 10)
        )

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM suspects WHERE id = %s",
            (suspect_id,)
        )

        suspect = cursor.fetchone()

        cursor.execute("""
            SELECT
                evidence.title,
                evidence.description,
                evidence.importance,
                evidence_connections.connection_description
            FROM evidence_connections
            JOIN evidence
                ON evidence_connections.evidence_id = evidence.id
            WHERE evidence_connections.suspect_id = %s
        """, (suspect_id,))

        connected_evidence = cursor.fetchall()

        cursor.close()
        connection.close()

        title = ctk.CTkLabel(
            self.main_frame,
            text=suspect["name"],
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )

        title.pack(
            anchor="w",
            padx=40,
            pady=(40, 5)
        )

        details = ctk.CTkLabel(
            self.main_frame,
            text=f'{suspect["age"]} years old  •  {suspect["occupation"]}',
            font=("Arial", 15),
            text_color="#7D8DA6"
        )

        details.pack(
            anchor="w",
            padx=40,
            pady=(0, 25)
        )

        # Information container
        info_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        info_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        # Motive
        motive_title = ctk.CTkLabel(
            info_frame,
            text="MOTIVE",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        motive_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        motive_text = ctk.CTkLabel(
            info_frame,
            text=suspect["motive"],
            font=("Arial", 14),
            text_color="#D5DCE8",
            justify="left",
            wraplength=800
        )

        motive_text.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # Alibi
        alibi_title = ctk.CTkLabel(
            info_frame,
            text="ALIBI",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        alibi_title.pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        alibi_text = ctk.CTkLabel(
            info_frame,
            text=suspect["alibi"],
            font=("Arial", 14),
            text_color="#D5DCE8",
            justify="left",
            wraplength=800
        )

        alibi_text.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # Connected evidence section
        evidence_title = ctk.CTkLabel(
            self.main_frame,
            text="CONNECTED EVIDENCE",
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )

        evidence_title.pack(
            anchor="w",
            padx=40,
            pady=(5, 10)
        )

        for evidence in connected_evidence:

            evidence_card = ctk.CTkFrame(
                self.main_frame,
                fg_color="#162235",
                corner_radius=12
            )

            evidence_card.pack(
                fill="x",
                padx=40,
                pady=6
            )

            evidence_name = ctk.CTkLabel(
                evidence_card,
                text=evidence["title"],
                font=("Arial", 16, "bold"),
                text_color="#FFFFFF"
            )

            evidence_name.pack(
                anchor="w",
                padx=20,
                pady=(15, 4)
            )

            connection_text = ctk.CTkLabel(
                evidence_card,
                text=evidence["connection_description"],
                font=("Arial", 13),
                text_color="#D5DCE8",
                justify="left",
                wraplength=800
            )

            connection_text.pack(
                anchor="w",
                padx=20,
                pady=(0, 15)
            )

    def create_evidence_page(self):

        title = ctk.CTkLabel(
            self.main_frame,
            text="Evidence",
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
            text="Collected evidence connected to CASE #042",
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

        cursor.execute("SELECT * FROM evidence")

        evidence_items = cursor.fetchall()

        print("Evidence count:", len(evidence_items))

        cursor.close()
        connection.close()

        for evidence in evidence_items:

            evidence_id = evidence["id"]

            card = ctk.CTkFrame(
                self.main_frame,
                fg_color="#162235",
                corner_radius=12,
                cursor="hand2"
            )

            card.pack(
                fill="x",
                padx=40,
                pady=8
            )

            title_label = ctk.CTkLabel(
                card,
                text=evidence["title"],
                font=("Arial", 18, "bold"),
                text_color="#FFFFFF"
            )

            title_label.pack(
                anchor="w",
                padx=20,
                pady=(15, 3)
            )

            details_label = ctk.CTkLabel(
                card,
                text=f'{evidence["evidence_type"]}  •  {evidence["location"]}',
                font=("Arial", 13),
                text_color="#7D8DA6"
            )

            details_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 8)
            )

            description_label = ctk.CTkLabel(
                card,
                text=evidence["description"],
                font=("Arial", 13),
                text_color="#D5DCE8",
                justify="left",
                wraplength=800
            )

            description_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 8)
            )

            importance_colors = {
                "Low": "#6B7280",
                "Medium": "#D4A72C",
                "High": "#E67E22",
                "Critical": "#E74C3C"
            }

            importance_label = ctk.CTkLabel(
                card,
                text=evidence["importance"].upper(),
                font=("Arial", 11, "bold"),
                text_color=importance_colors.get(
                    evidence["importance"],
                    "#7FA9D8"
                )
            )

            importance_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 15)
            )

            def open_evidence(event, evidence_id=evidence_id):
                self.show_evidence_details(evidence_id)
                return "break"


            widgets = [
                card,
                title_label,
                details_label,
                description_label,
                importance_label
            ]

            for widget in widgets:
                widget.bind(
                    "<Button-1>",
                    open_evidence
                )

    def show_evidence_details(self, evidence_id):

        self.investigated_evidence.add(evidence_id)

        # Clear current page
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.main_frame._parent_canvas.yview_moveto(0)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM evidence WHERE id = %s",
            (evidence_id,)
        )

        evidence = cursor.fetchone()

        # Back button FIRST
        back_button = ctk.CTkButton(
            self.main_frame,
            text="← Back to Evidence",
            width=160,
            height=38,
            fg_color="transparent",
            hover_color="#162235",
            text_color="#7FA9D8",
            anchor="w",
            command=lambda: self.show_page("evidence")
        )

        back_button.pack(
            anchor="w",
            padx=40,
            pady=(30, 10)
        )

        cursor.close()
        connection.close()

        # Safety check
        if evidence is None:
            return

        # Evidence title
        title = ctk.CTkLabel(
            self.main_frame,
            text=evidence["title"],
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )

        title.pack(
            anchor="w",
            padx=40,
            pady=(5, 20)
        )

        # Information frame
        info_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        info_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        details_title = ctk.CTkLabel(
            info_frame,
            text="EVIDENCE DETAILS",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        details_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        # Evidence type
        type_label = ctk.CTkLabel(
            info_frame,
            text=f"Type: {evidence['evidence_type']}",
            font=("Arial", 14),
            text_color="#D5DCE8",
            anchor="w"
        )
        type_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        # Location
        location_label = ctk.CTkLabel(
            info_frame,
            text=f"Location: {evidence['location']}",
            font=("Arial", 14),
            text_color="#D5DCE8",
            anchor="w"
        )
        location_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        # Importance
        importance_colors = {
            "Low": "#6B7280",
            "Medium": "#D4A72C",
            "High": "#E67E22",
            "Critical": "#E74C3C"
        }
        importance_label = ctk.CTkLabel(
            info_frame,
            text=f"Importance: {evidence['importance'].upper()}",
            font=("Arial", 14, "bold"),
            text_color=importance_colors.get(
                evidence['importance'],
                "#7FA9D8"
            ),
            anchor="w"
        )
        importance_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        # Description frame
        desc_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )
        desc_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        # Description title
        desc_title = ctk.CTkLabel(
            desc_frame,
            text="DESCRIPTION",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8",
            anchor="w"
        )
        desc_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        # Description text
        desc_text = ctk.CTkLabel(
            desc_frame,
            text=evidence['description'],
            font=("Arial", 14),
            text_color="#D5DCE8",
            justify="left",
            wraplength=800,
            anchor="w"
        )
        desc_text.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # Connect Evidence button
        connect_button = ctk.CTkButton(
            self.main_frame,
            text="CONNECT EVIDENCE",
            width=180,
            height=38,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=lambda: self.show_connection_modal(evidence_id)
        )

        connect_button.pack(
            anchor="w",
            padx=40,
            pady=(10, 20)
        )

    def show_connection_modal(self, current_evidence_id):
        # Get all evidence items
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evidence")
        all_evidence = cursor.fetchall()
        cursor.close()
        connection.close()

        # Create modal
        modal = ctk.CTkFrame(
            self,
            width=500,
            height=400,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Modal title
        modal_title = ctk.CTkLabel(
            modal,
            text="CONNECT EVIDENCE",
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )
        modal_title.pack(
            pady=(25, 15)
        )

        # Instruction text
        instruction = ctk.CTkLabel(
            modal,
            text="Select another piece of evidence to connect with:",
            font=("Arial", 13),
            text_color="#7D8DA6"
        )
        instruction.pack(
            pady=(0, 15)
        )

        # Evidence selection frame
        selection_frame = ctk.CTkFrame(
            modal,
            fg_color="#162235",
            corner_radius=10
        )
        selection_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 15)
        )

        # Add evidence items (excluding current)
        for evidence in all_evidence:
            if evidence["id"] == current_evidence_id:
                continue

            evidence_button = ctk.CTkButton(
                selection_frame,
                text=evidence["title"],
                font=("Arial", 13),
                fg_color="transparent",
                hover_color="#1C2C44",
                text_color="#D5DCE8",
                anchor="w",
                height=35,
                command=lambda e=evidence, ce=current_evidence_id, m=modal: self.check_connection(e["id"], ce, m)
            )
            evidence_button.pack(
                fill="x",
                padx=15,
                pady=5
            )

        # Cancel button
        cancel_button = ctk.CTkButton(
            modal,
            text="CANCEL",
            width=120,
            height=35,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=modal.destroy
        )
        cancel_button.pack(
            pady=(0, 20)
        )

    def check_connection(self, selected_evidence_id, current_evidence_id, modal):
        modal.destroy()

        # Check if this is a valid connection
        connection_key = frozenset({current_evidence_id, selected_evidence_id})
        
        if connection_key in self.valid_connections:
            connection_data = self.valid_connections[connection_key]
            
            # Check if already discovered
            if connection_data["id"] in self.discovered_leads:
                self.show_already_discovered_modal(connection_data["title"])
            else:
                # Add to discovered leads
                self.discovered_leads.add(connection_data["id"])
                self.show_connection_discovered_modal(connection_data)
        else:
            # Invalid connection
            self.show_invalid_connection_modal()

    def show_connection_discovered_modal(self, connection_data):
        modal = ctk.CTkFrame(
            self,
            width=450,
            height=250,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Title
        title = ctk.CTkLabel(
            modal,
            text="CONNECTION DISCOVERED",
            font=("Arial", 20, "bold"),
            text_color="#D4A72C"
        )
        title.pack(
            pady=(30, 15)
        )

        # Lead title
        lead_title = ctk.CTkLabel(
            modal,
            text=connection_data["title"],
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        )
        lead_title.pack(
            pady=(0, 10)
        )

        # Description
        description = ctk.CTkLabel(
            modal,
            text=connection_data["description"],
            font=("Arial", 13),
            text_color="#D5DCE8",
            wraplength=380,
            justify="center"
        )
        description.pack(
            padx=30,
            pady=(0, 20)
        )

        # Continue button
        continue_button = ctk.CTkButton(
            modal,
            text="CONTINUE",
            width=130,
            height=38,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=modal.destroy
        )
        continue_button.pack()

    def show_invalid_connection_modal(self):
        modal = ctk.CTkFrame(
            self,
            width=400,
            height=180,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Message
        message = ctk.CTkLabel(
            modal,
            text="No meaningful connection can be established\nfrom these pieces of evidence.",
            font=("Arial", 14),
            text_color="#7D8DA6",
            justify="center"
        )
        message.pack(
            pady=(40, 20)
        )

        # Close button
        close_button = ctk.CTkButton(
            modal,
            text="CLOSE",
            width=100,
            height=35,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=modal.destroy
        )
        close_button.pack()

    def show_already_discovered_modal(self, connection_title):
        modal = ctk.CTkFrame(
            self,
            width=400,
            height=180,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Message
        message = ctk.CTkLabel(
            modal,
            text=f"This connection has already been documented:\n{connection_title}",
            font=("Arial", 14),
            text_color="#7D8DA6",
            justify="center"
        )
        message.pack(
            pady=(40, 20)
        )

        # Close button
        close_button = ctk.CTkButton(
            modal,
            text="CLOSE",
            width=100,
            height=35,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=modal.destroy
        )
        close_button.pack()

    def create_deduction_board_page(self):

        title = ctk.CTkLabel(
            self.main_frame,
            text="Deduction Board",
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
            text="Document connections and deductions discovered from evidence analysis",
            font=("Arial", 14),
            text_color="#7D8DA6"
        )

        subtitle.pack(
            anchor="w",
            padx=40,
            pady=(0, 25)
        )

        # Check if there are discovered leads
        if not self.discovered_leads:
            # Show empty state
            empty_state_frame = ctk.CTkFrame(
                self.main_frame,
                fg_color="#162235",
                corner_radius=12
            )

            empty_state_frame.pack(
                fill="x",
                padx=40,
                pady=(0, 15)
            )

            # Empty state icon/text
            empty_title = ctk.CTkLabel(
                empty_state_frame,
                text="No deductions discovered",
                font=("Arial", 18, "bold"),
                text_color="#7D8DA6"
            )

            empty_title.pack(
                pady=(40, 10)
            )

            empty_description = ctk.CTkLabel(
                empty_state_frame,
                text="Examine the evidence and connect related clues to uncover hidden relationships.",
                font=("Arial", 14),
                text_color="#8B9BB4",
                wraplength=800,
                justify="center"
            )

            empty_description.pack(
                padx=40,
                pady=(0, 40)
            )
        else:
            # Get evidence data for display
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM evidence")
            evidence_data = {e["id"]: e for e in cursor.fetchall()}
            cursor.close()
            connection.close()

            # Display discovered deductions
            for connection_key, connection_data in self.valid_connections.items():
                if connection_data["id"] in self.discovered_leads:
                    # Get evidence IDs from the connection
                    evidence_ids = list(connection_data["evidence_ids"])
                    
                    # Get evidence names
                    evidence_names = []
                    for eid in evidence_ids:
                        if eid in evidence_data:
                            evidence_names.append(evidence_data[eid]["title"])
                    
                    # Create deduction card
                    deduction_card = ctk.CTkFrame(
                        self.main_frame,
                        fg_color="#162235",
                        corner_radius=12
                    )

                    deduction_card.pack(
                        fill="x",
                        padx=40,
                        pady=(0, 15)
                    )

                    # Deduction header
                    deduction_header = ctk.CTkLabel(
                        deduction_card,
                        text="DEDUCTION",
                        font=("Arial", 13, "bold"),
                        text_color="#7FA9D8"
                    )

                    deduction_header.pack(
                        anchor="w",
                        padx=20,
                        pady=(18, 12)
                    )

                    # Evidence connection display
                    if len(evidence_names) >= 2:
                        evidence_frame = ctk.CTkFrame(
                            deduction_card,
                            fg_color="transparent"
                        )

                        evidence_frame.pack(
                            fill="x",
                            padx=20,
                            pady=(0, 12)
                        )

                        # First evidence
                        evidence1_label = ctk.CTkLabel(
                            evidence_frame,
                            text=evidence_names[0],
                            font=("Arial", 14, "bold"),
                            text_color="#FFFFFF"
                        )
                        evidence1_label.pack(
                            anchor="w",
                            pady=(0, 5)
                        )

                        # Plus sign
                        plus_label = ctk.CTkLabel(
                            evidence_frame,
                            text="+",
                            font=("Arial", 16, "bold"),
                            text_color="#7FA9D8"
                        )
                        plus_label.pack(
                            anchor="w",
                            pady=(0, 5)
                        )

                        # Second evidence
                        evidence2_label = ctk.CTkLabel(
                            evidence_frame,
                            text=evidence_names[1],
                            font=("Arial", 14, "bold"),
                            text_color="#FFFFFF"
                        )
                        evidence2_label.pack(
                            anchor="w",
                            pady=(0, 5)
                        )

                        # Arrow
                        arrow_label = ctk.CTkLabel(
                            evidence_frame,
                            text="↓",
                            font=("Arial", 16, "bold"),
                            text_color="#7FA9D8"
                        )
                        arrow_label.pack(
                            anchor="w",
                            pady=(0, 5)
                        )

                    # Deduction title
                    result_title = ctk.CTkLabel(
                        deduction_card,
                        text=connection_data["title"],
                        font=("Arial", 16, "bold"),
                        text_color="#D4A72C"
                    )

                    result_title.pack(
                        anchor="w",
                        padx=20,
                        pady=(0, 10)
                    )

                    # Deduction description
                    result_description = ctk.CTkLabel(
                        deduction_card,
                        text=connection_data["description"],
                        font=("Arial", 14),
                        text_color="#D5DCE8",
                        justify="left",
                        wraplength=800,
                        anchor="w"
                    )

                    result_description.pack(
                        anchor="w",
                        padx=20,
                        pady=(0, 18)
                    )

    def create_timeline_page(self):

        title = ctk.CTkLabel(
            self.main_frame,
            text="Timeline",
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
            text="Chronological reconstruction of events",
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

        cursor.execute("""
            SELECT * FROM timeline
            ORDER BY event_time
        """)

        events = cursor.fetchall()

        cursor.close()
        connection.close()

        for event in events:

            timeline_row = ctk.CTkFrame(
                self.main_frame,
                fg_color="transparent"
            )

            timeline_row.pack(
                fill="x",
                padx=40,
                pady=3
            )

            dot = ctk.CTkLabel(
                timeline_row,
                text="●",
                font=("Arial", 20),
                text_color="#7FA9D8",
                width=35
            )

            dot.pack(
                side="left",
                padx=(0, 10)
            )

            event_frame = ctk.CTkFrame(
                timeline_row,
                fg_color="#162235",
                corner_radius=12
            )

            event_frame.pack(
                side="left",
                fill="x",
                expand=True
            )

            time_label = ctk.CTkLabel(
                event_frame,
                text=str(event["event_time"]),
                font=("Arial", 18, "bold"),
                text_color="#7FA9D8",
                width=100
            )

            time_label.pack(
                side="left",
                padx=(20, 15),
                pady=20
            )

            details_frame = ctk.CTkFrame(
                event_frame,
                fg_color="transparent"
            )

            details_frame.pack(
                side="left",
                fill="both",
                expand=True,
                pady=15
            )

            event_label = ctk.CTkLabel(
                details_frame,
                text=event["event"],
                font=("Arial", 14),
                text_color="#FFFFFF",
                justify="left",
                wraplength=650
            )

            event_label.pack(
                anchor="w"
            )

            location_label = ctk.CTkLabel(
                details_frame,
                text=event["location"],
                font=("Arial", 12),
                text_color="#7D8DA6"
            )

            location_label.pack(
                anchor="w",
                pady=(5, 0)
            )

if __name__ == "__main__":
    app = CaseFileApp()
    app.mainloop()