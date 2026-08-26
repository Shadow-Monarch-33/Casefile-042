import customtkinter as ctk
from database import get_connection
from functools import partial

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CaseFileApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_page = "case overview"
        self.investigated_evidence = set()
        self.discovered_leads = set()
        self.discovery_history = []
        self.asked_questions = {}
        self.nav_button_rows = {}
        self.nav_buttons = {}
        self.nav_badges = {}
        self.page_config = {
            "case overview": {"label": "Case Overview", "icon": "▣"},
            "suspects": {"label": "Suspects", "icon": "◉"},
            "evidence": {"label": "Evidence", "icon": "⌕"},
            "timeline": {"label": "Timeline", "icon": "◷"},
            "deduction board": {"label": "Case Findings", "icon": "✦"}
        }
        self.valid_connections = {
            frozenset({1, 4}): {
                "id": "access_during_blackout",
                "title": "ACCESS DURING BLACKOUT",
                "description": (
                    "The access card activity occurred while "
                    "the executive floor security cameras were offline."
                ),
                "evidence_ids": {1, 4},
                "connection_type": "Timeline"
            },
            frozenset({4, 7}): {
                "id": "security_override_access",
                "title": "SECURITY-LEVEL OVERRIDE",
                "description": (
                    "The executive floor blackout was triggered through a "
                    "security administrator login, not a random system failure."
                ),
                "evidence_ids": {4, 7},
                "connection_type": "Access / System"
            },
            frozenset({5, 6}): {
                "id": "marcus_unverified_window",
                "title": "MARCUS UNACCOUNTED FOR",
                "description": (
                    "Marcus's meeting ended before the 10:24 PM struggle, "
                    "leaving his movements unverified during a critical window."
                ),
                "evidence_ids": {5, 6},
                "connection_type": "Timeline"
            }
        }

        self.interview_questions = {
            1: [  # Elena Vasquez
                {
                    "id": "elena_q1",
                    "question": "Where were you between 10:00 PM and 10:30 PM?",
                    "answer": "I left the office around 9:40 PM and went straight home. I was there all evening.",
                    "requires": None
                },
                {
                    "id": "elena_q2",
                    "question": "Did you access the executive floor that night?",
                    "answer": "No, I left before 10 PM. I haven't been back to the office since.",
                    "requires": None
                },
                {
                    "id": "elena_q3",
                    "question": "Why was your access card used during the security blackout?",
                    "answer": "That's impossible. I had my card with me at home. Someone must have used a duplicate or found a way to clone it.",
                    "requires": "access_during_blackout"
                }
            ],
            2: [  # Marcus Reid
                {
                    "id": "marcus_q1",
                    "question": "Where were you between 10:00 PM and 10:30 PM?",
                    "answer": "I was in a meeting with investors in the conference room. It lasted until 10:30 PM.",
                    "requires": None
                },
                {
                    "id": "marcus_q2",
                    "question": "Can anyone confirm your whereabouts during that time?",
                    "answer": "The investors I was meeting with can confirm I was there the entire time.",
                    "requires": None
                },
                {
                    "id": "marcus_q3",
                    "question": "Why did you lie about the investor meeting ending at 10:30 PM?",
                    "answer": "Okay, fine. The meeting ended early at 10:08 PM. I didn't want to admit they rejected our proposal. I was walking around the building to clear my head, but I didn't go to the executive floor!",
                    "requires": "marcus_meeting_lie"
                },
                {
                    "id": "marcus_q4",
                    "question": "What were you doing when the struggle likely happened at 10:24 PM?",
                    "answer": "I was alone after the meeting ended. I kept walking the lower offices because I didn't want anyone seeing how badly the investors shut me down.",
                    "requires": "marcus_unverified_window"
                }
            ],
            3: [  # Noah Bennett
                {
                    "id": "noah_q1",
                    "question": "Where were you between 10:00 PM and 10:30 PM?",
                    "answer": "I was working alone in the server room. I had a lot of code to review before the deadline.",
                    "requires": None
                },
                {
                    "id": "noah_q2",
                    "question": "Did you leave the server room at any point?",
                    "answer": "No, I stayed there continuously until around 10:45 PM when I finished my work.",
                    "requires": None
                }
            ],
            4: [  # Sophie Laurent
                {
                    "id": "sophie_q1",
                    "question": "Where were you between 10:00 PM and 10:30 PM?",
                    "answer": "I was in the security office reviewing CCTV footage from earlier in the day.",
                    "requires": None
                },
                {
                    "id": "sophie_q2",
                    "question": "Did you notice anything unusual with the security systems?",
                    "answer": "Everything seemed normal when I checked. The systems were running as expected.",
                    "requires": None
                },
                {
                    "id": "sophie_q3",
                    "question": "If you were in the security office, why was your lipstick on a cup in the victim's office?",
                    "answer": "I... I was there earlier, around 9:30 PM, to discuss access log audits. I must have left my coffee cup. I was back in the security office during the blackout, I swear.",
                    "requires": "sophie_office_presence"
                },
                {
                    "id": "sophie_q4",
                    "question": "Who could have triggered the 10:10 PM security override?",
                    "answer": "Only someone using a security administrator session. That console should have been locked down, but anyone sitting at an active security desk could have used it.",
                    "requires": "security_override_access"
                }
            ]
        }

        self.contradictions = {
            "elena_q2": {
                "evidence_id": 1,
                "deduction_id": "elena_access_lie",
                "title": "ELENA'S FALSE ALIBI",
                "description": "Elena claims she left before 10 PM and didn't access the executive floor, but her access card was used at 10:12 PM."
            },
            "marcus_q1": {
                "evidence_id": 6,
                "deduction_id": "marcus_meeting_lie",
                "title": "MARCUS'S SHORT MEETING",
                "description": "Marcus claims his meeting lasted until 10:30 PM, but records show it ended at 10:08 PM."
            },
            "sophie_q1": {
                "evidence_id": 8,
                "deduction_id": "sophie_office_presence",
                "title": "SOPHIE IN THE OFFICE",
                "description": "Sophie claims she was in the security office, but her lipstick was found in the victim's office."
            }
        }

        self.additional_findings = {}
        self.findings_metadata = {}
        self.rebuild_findings_metadata()

        self.title("CASEFILE")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.create_layout()
        self.update_case_progress()

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

        self.build_sidebar_navigation()

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
        self.current_page = page_name
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.main_frame._parent_canvas.yview_moveto(0)
        self.update_nav_state()

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

    def build_sidebar_navigation(self):
        nav_items = [
            "case overview",
            "suspects",
            "evidence",
            "timeline",
            "deduction board"
        ]

        for index, page_name in enumerate(nav_items):
            row = ctk.CTkFrame(
                self.sidebar,
                fg_color="transparent",
                corner_radius=10,
                border_width=1,                
            )
            row.pack(fill="x", padx=15, pady=(0, 8) if index == 0 else 8)

            button = ctk.CTkButton(
                row,
                text=f'{self.page_config[page_name]["icon"]}  {self.page_config[page_name]["label"]}',
                font=("Arial", 15),
                anchor="w",
                height=45,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#16345C",
                text_color="#D5DCE8",
                command=lambda target=page_name: self.show_page(target)
            )
            button.pack(side="left", fill="x", expand=True, padx=(0, 8))

            badge = ctk.CTkLabel(
                row,
                text="",
                width=34,
                height=24,
                corner_radius=12,
                font=("Arial", 11, "bold"),
                fg_color="#1C2C44",
                text_color="#7FA9D8"
            )
            if page_name == "deduction board":
                badge.pack(side="right", padx=(0, 6))
                self.deduction_board_button = button

            self.nav_button_rows[page_name] = row
            self.nav_buttons[page_name] = button
            self.nav_badges[page_name] = badge

    def update_nav_state(self):
        for page_name, button in self.nav_buttons.items():
            is_active = page_name == self.current_page
            self.nav_button_rows[page_name].configure(
                fg_color="#16345C" if is_active else "transparent",
                border_color="#2C507F" if is_active else "#202020"
            )
            button.configure(
                fg_color="#16345C" if is_active else "transparent",
                text_color="#FFFFFF" if is_active else "#D5DCE8"
            )

    def rebuild_findings_metadata(self):
        findings = {}

        for connection_data in self.valid_connections.values():
            findings[connection_data["id"]] = {
                "title": connection_data["title"],
                "description": connection_data["description"],
                "source_type": "evidence_connection",
                "evidence_ids": list(connection_data["evidence_ids"])
            }

        for contradiction in self.contradictions.values():
            findings[contradiction["deduction_id"]] = {
                "title": contradiction["title"],
                "description": contradiction["description"],
                "source_type": "contradiction",
                "evidence_ids": [contradiction["evidence_id"]]
            }

        findings.update(self.additional_findings)
        self.findings_metadata = findings

    def update_case_progress(self):
        if "deduction board" not in self.nav_badges:
            return

        findings_count = len(self.discovered_leads)
        badge = self.nav_badges["deduction board"]
        if findings_count:
            badge.configure(text=str(findings_count), fg_color="#1C2C44", text_color="#FFFFFF")
            badge.pack(side="right", padx=(0, 6))
        else:
            badge.pack_forget()

    def discover_finding(self, finding_id):
        if finding_id in self.discovered_leads:
            return []

        self.discovered_leads.add(finding_id)
        self.discovery_history.append(finding_id)
        self.update_case_progress()
        return self.get_newly_unlocked_questions(finding_id)

    def get_discovered_findings(self):
        ordered_findings = []

        for finding_id in reversed(self.discovery_history):
            if finding_id in self.discovered_leads and finding_id not in ordered_findings:
                ordered_findings.append(finding_id)

        for finding_id in sorted(self.discovered_leads):
            if finding_id not in ordered_findings:
                ordered_findings.append(finding_id)

        return ordered_findings

    def is_requirement_met(self, requires):
        if requires is None:
            return True
        if isinstance(requires, (list, tuple, set)):
            return all(requirement in self.discovered_leads for requirement in requires)
        return requires in self.discovered_leads

    def get_question_status(self, suspect_id, question_data):
        question_id = question_data["id"]
        asked_questions = self.asked_questions.setdefault(suspect_id, set())

        if not self.is_requirement_met(question_data.get("requires")):
            return "LOCKED"
        if question_id in asked_questions:
            return "ASKED"
        return "AVAILABLE"

    def get_available_question_count(self, suspect_id):
        questions = self.interview_questions.get(suspect_id, [])
        return sum(1 for question in questions if self.is_requirement_met(question.get("requires")))

    def get_asked_question_count(self, suspect_id):
        return len(self.asked_questions.get(suspect_id, set()))

    def get_total_asked_questions(self):
        return sum(len(question_ids) for question_ids in self.asked_questions.values())

    def get_total_available_questions(self):
        return sum(self.get_available_question_count(suspect_id) for suspect_id in self.interview_questions)

    def get_total_question_count(self):
        return sum(len(questions) for questions in self.interview_questions.values())

    def get_interviewed_suspect_count(self):
        return sum(1 for question_ids in self.asked_questions.values() if question_ids)

    def get_newly_unlocked_questions(self, finding_id):
        unlocked = []
        for suspect_id, questions in self.interview_questions.items():
            for question_data in questions:
                if question_data.get("requires") == finding_id:
                    unlocked.append({"suspect_id": suspect_id, "question_id": question_data["id"]})
        return unlocked

    def get_suspect_name(self, suspect_id):
        suspects = {
            1: "Elena Vasquez",
            2: "Marcus Reid",
            3: "Noah Bennett",
            4: "Sophie Laurent"
        }
        return suspects.get(suspect_id, "Unknown Suspect")

    def get_evidence_lookup(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, title FROM evidence")
        evidence_lookup = {evidence["id"]: evidence["title"] for evidence in cursor.fetchall()}
        cursor.close()
        connection.close()
        return evidence_lookup

    def get_finding_label(self, source_type):
        labels = {
            "evidence_connection": "EVIDENCE CONNECTION",
            "contradiction": "CONTRADICTION",
            "interview": "INTERVIEW LEAD"
        }
        return labels.get(source_type, "CASE FINDING")

    def get_related_evidence_titles(self, finding_data, evidence_lookup):
        evidence_ids = finding_data.get("evidence_ids", [])
        return [evidence_lookup[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence_lookup]

    def create_page_header(self, title, subtitle, section_name):
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(36, 16))

        breadcrumb = ctk.CTkLabel(
            header,
            text=f"CASEFILE / {section_name.upper()}",
            font=("Arial", 12, "bold"),
            text_color="#7FA9D8"
        )
        breadcrumb.pack(anchor="w")

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w", pady=(6, 4))

        subtitle_label = ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Arial", 14),
            text_color="#8B9BB4"
        )
        subtitle_label.pack(anchor="w")

    def get_next_lead_text(self):
        for suspect_id, questions in self.interview_questions.items():
            for question_data in questions:
                if self.get_question_status(suspect_id, question_data) == "AVAILABLE" and question_data["id"] not in self.asked_questions.get(suspect_id, set()):
                    return f"Revisit {self.get_suspect_name(suspect_id)} to push a newly available interview angle."

        for connection_data in self.valid_connections.values():
            if connection_data["id"] not in self.discovered_leads:
                return "Cross-check open evidence to uncover another connection for the case findings board."

        return "Review documented findings and challenge suspect statements with matching evidence."

    def open_case_findings(self, widgets_to_close=None):
        if widgets_to_close:
            for widget in widgets_to_close:
                if widget and widget.winfo_exists():
                    widget.destroy()
        self.show_page("deduction board")

    def show_discovery_modal(self, finding_id, widgets_to_close=None, unlocked_questions=None):
        finding_data = self.findings_metadata.get(finding_id)
        if not finding_data:
            return

        modal = ctk.CTkFrame(
            self,
            width=520,
            height=310,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            modal,
            text="NEW LEAD DISCOVERED",
            font=("Arial", 16, "bold"),
            text_color="#D4A72C"
        )
        title.pack(pady=(30, 12))

        source_label = ctk.CTkLabel(
            modal,
            text=self.get_finding_label(finding_data["source_type"]),
            font=("Arial", 11, "bold"),
            text_color="#7FA9D8"
        )
        source_label.pack(pady=(0, 10))

        finding_title = ctk.CTkLabel(
            modal,
            text=finding_data["title"],
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )
        finding_title.pack(pady=(0, 10))

        description = ctk.CTkLabel(
            modal,
            text=finding_data["description"],
            font=("Arial", 14),
            text_color="#D5DCE8",
            wraplength=420,
            justify="center"
        )
        description.pack(padx=35, pady=(0, 25))

        if unlocked_questions:
            unlocked_suspects = []
            for question_data in unlocked_questions:
                suspect_name = self.get_suspect_name(question_data["suspect_id"])
                if suspect_name not in unlocked_suspects:
                    unlocked_suspects.append(suspect_name)

            unlock_label = ctk.CTkLabel(
                modal,
                text="NEW QUESTION AVAILABLE  •  " + ", ".join(unlocked_suspects),
                font=("Arial", 11, "bold"),
                text_color="#7FA9D8",
                fg_color="#162235",
                corner_radius=10,
                padx=12,
                pady=6
            )
            unlock_label.pack(pady=(0, 18))

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(pady=(0, 28))

        view_button = ctk.CTkButton(
            actions,
            text="VIEW CASE FINDINGS",
            width=180,
            height=40,
            fg_color="#1D4E89",
            hover_color="#2863A8",
            text_color="#FFFFFF",
            command=lambda: self.open_case_findings([modal] + (widgets_to_close or []))
        )
        view_button.pack(side="left", padx=(0, 8))

        continue_button = ctk.CTkButton(
            actions,
            text="CONTINUE",
            width=120,
            height=40,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            command=modal.destroy
        )
        continue_button.pack(side="left", padx=(8, 0))

    def create_overview_page(self):
        self.create_page_header(
            "The Last Access",
            "Investigation headquarters for CASE #042.",
            "Case Overview"
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
            (str(len(self.discovered_leads)), "FINDINGS LOGGED"),
            (str(len(self.investigated_evidence)), "EVIDENCE REVIEWED"),
            (str(self.get_interviewed_suspect_count()), "SUSPECTS INTERVIEWED"),
            (f"{self.get_total_asked_questions()} / {self.get_total_question_count()}", "QUESTIONS ASKED")
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

        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        status_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        leads_title = ctk.CTkLabel(
            status_frame,
            text="INVESTIGATION STATUS",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        leads_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        leads = [
            f"Case findings documented: {len(self.discovered_leads)} of {len(self.valid_connections) + len(self.contradictions)} known breakthroughs.",
            f"Questions currently available: {self.get_total_available_questions()} across {suspect_count} suspects.",
            f"Critical evidence in play: {critical_count} items tied to the murder window."
        ]

        for lead in leads:
            lead_label = ctk.CTkLabel(
                status_frame,
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

        next_lead_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        next_lead_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 30)
        )

        next_lead_title = ctk.CTkLabel(
            next_lead_frame,
            text="NEXT LEAD",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )

        next_lead_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        next_lead_label = ctk.CTkLabel(
            next_lead_frame,
            text=self.get_next_lead_text(),
            font=("Arial", 15),
            text_color="#FFFFFF",
            justify="left",
            wraplength=800
        )

        next_lead_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        discovered_findings = self.get_discovered_findings()
        if discovered_findings:
            recent_finding = self.findings_metadata.get(discovered_findings[0])
            if recent_finding:
                recent_label = ctk.CTkLabel(
                    next_lead_frame,
                    text=f"RECENT DISCOVERY  •  {recent_finding['title']}",
                    font=("Arial", 12, "bold"),
                    text_color="#D4A72C"
                )
                recent_label.pack(
                    anchor="w",
                    padx=20,
                    pady=(0, 18)
                )
        else:
            starter_label = ctk.CTkLabel(
                next_lead_frame,
                text="Start by opening critical evidence and questioning suspects to build your first findings.",
                font=("Arial", 12),
                text_color="#8B9BB4",
                justify="left",
                wraplength=800
            )
            starter_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 18)
            )

    def create_suspects_page(self):
        self.create_page_header(
            "Suspects",
            "Individuals connected to CASE #042.",
            "Suspects"
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
                corner_radius=12,
                border_width=1,
                border_color="#22354E"
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
                pady=(0, 10)
            )

            available_questions = self.get_available_question_count(suspect["id"])
            total_questions = len(self.interview_questions.get(suspect["id"], []))
            asked_questions = self.get_asked_question_count(suspect["id"])

            progress_label = ctk.CTkLabel(
                card,
                text=f"INTERVIEW  •  {available_questions}/{total_questions} AVAILABLE  •  {asked_questions} ASKED",
                font=("Arial", 11, "bold"),
                text_color="#8B9BB4"
            )

            progress_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 12)
            )

            view_button = ctk.CTkButton(
                card,
                text="OPEN PROFILE  →",
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

        self.main_frame._parent_canvas.yview_moveto(0)

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

        self.create_page_header(
            suspect["name"],
            f'{suspect["age"]} years old  •  {suspect["occupation"]}',
            "Suspects"
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

        # Interview section
        interview_title = ctk.CTkLabel(
            self.main_frame,
            text="INTERVIEW",
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )

        interview_title.pack(
            anchor="w",
            padx=40,
            pady=(20, 5)
        )

        interview_subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Question the suspect and investigate inconsistencies in their statements.",
            font=("Arial", 13),
            text_color="#7D8DA6"
        )

        interview_subtitle.pack(
            anchor="w",
            padx=40,
            pady=(0, 12)
        )

        progress_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#162235",
            corner_radius=12
        )

        progress_frame.pack(
            anchor="w",
            padx=40,
            pady=(0, 20)
        )

        progress_title = ctk.CTkLabel(
            progress_frame,
            text="INTERVIEW PROGRESS",
            font=("Arial", 12, "bold"),
            text_color="#7FA9D8"
        )

        progress_title.pack(
            anchor="w",
            padx=18,
            pady=(14, 4)
        )

        available_questions = self.get_available_question_count(suspect_id)
        total_questions = len(self.interview_questions.get(suspect_id, []))
        asked_questions = len(self.asked_questions.get(suspect_id, set()))

        progress_text = ctk.CTkLabel(
            progress_frame,
            text=f"{available_questions} / {total_questions} QUESTIONS AVAILABLE  •  {asked_questions} ASKED",
            font=("Arial", 13),
            text_color="#D5DCE8"
        )

        progress_text.pack(
            anchor="w",
            padx=18,
            pady=(0, 14)
        )

        # Begin Interview button
        interview_button = ctk.CTkButton(
            self.main_frame,
            text="BEGIN INTERVIEW",
            width=200,
            height=45,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=lambda: self.show_interview(suspect_id, suspect["name"])
        )

        interview_button.pack(
            anchor="w",
            padx=40,
            pady=(0, 30)
        )

    def show_interview(self, suspect_id, suspect_name):
        # Get interview questions for this suspect
        questions = self.interview_questions.get(suspect_id, [])

        # Track asked questions for this runtime session
        asked_questions = self.asked_questions.setdefault(suspect_id, set())
        current_question_index = [0]  # Use list for mutability in nested functions
        current_typing = {"id": None}

        # Create interview modal
        modal = ctk.CTkFrame(
            self,
            width=700,
            height=600,
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

        # Header section
        header_label = ctk.CTkLabel(
            modal,
            text="INTERVIEW RECORD",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )
        header_label.pack(
            pady=(25, 8)
        )

        suspect_label = ctk.CTkLabel(
            modal,
            text=suspect_name.upper(),
            font=("Arial", 24, "bold"),
            text_color="#FFFFFF"
        )
        suspect_label.pack(
            pady=(0, 20)
        )

        # Divider
        divider = ctk.CTkFrame(
            modal,
            fg_color="#2A3D57",
            height=1
        )
        divider.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        # Question display frame
        question_frame = ctk.CTkFrame(
            modal,
            fg_color="#162235",
            corner_radius=12
        )
        question_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        # Question counter
        counter_label = ctk.CTkLabel(
            question_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#7FA9D8"
        )
        counter_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        # Question text
        question_label = ctk.CTkLabel(
            question_frame,
            text="",
            font=("Arial", 16),
            text_color="#FFFFFF",
            justify="center",
            wraplength=600
        )
        question_label.pack(
            padx=20,
            pady=(0, 15)
        )

        # Ask button
        ask_button = ctk.CTkButton(
            question_frame,
            text="ASK QUESTION",
            width=160,
            height=38,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"),
            corner_radius=8
        )
        ask_button.pack(
            pady=(0, 15)
        )

        # Response section
        response_frame = ctk.CTkFrame(
            modal,
            fg_color="#162235",
            corner_radius=12
        )
        response_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        response_title = ctk.CTkLabel(
            response_frame,
            text="RESPONSE",
            font=("Arial", 12, "bold"),
            text_color="#7FA9D8"
        )
        response_title.pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        response_label = ctk.CTkLabel(
            response_frame,
            text="",
            font=("Arial", 14),
            text_color="#D5DCE8",
            justify="left",
            wraplength=600,
            anchor="w"
        )
        response_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        present_evidence_button = ctk.CTkButton(
            response_frame,
            text="PRESENT EVIDENCE",
            width=160,
            height=32,
            fg_color="#1D4E89",
            hover_color="#2863A8",
            text_color="#FFFFFF",
            font=("Arial", 12, "bold"),
            corner_radius=8
        )
        # Hidden initially

        # Navigation buttons
        nav_frame = ctk.CTkFrame(
            modal,
            fg_color="transparent"
        )
        nav_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        def navigate(direction):
            if current_typing.get("id"):
                self.after_cancel(current_typing["id"])
                current_typing["id"] = None
            current_question_index[0] += direction
            current_question_index[0] = max(0, min(current_question_index[0], len(questions) - 1))
            update_question_display()

        prev_button = ctk.CTkButton(
            nav_frame,
            text="← PREVIOUS",
            width=120,
            height=35,
            fg_color="transparent",
            hover_color="#1C2C44",
            text_color="#7D8DA6",
            corner_radius=8,
            command=lambda: navigate(-1)
        )
        prev_button.pack(
            side="left"
        )

        next_button = ctk.CTkButton(
            nav_frame,
            text="NEXT →",
            width=120,
            height=35,
            fg_color="transparent",
            hover_color="#1C2C44",
            text_color="#7D8DA6",
            corner_radius=8,
            command=lambda: navigate(1)
        )
        next_button.pack(
            side="right"
        )

        def close_modal():
            if current_typing.get("id"):
                self.after_cancel(current_typing["id"])
            modal.destroy()

        # Exit button
        exit_button = ctk.CTkButton(
            modal,
            text="EXIT INTERVIEW",
            width=160,
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color="#2A3D57",
            hover_color="#1C2C44",
            text_color="#7D8DA6",
            corner_radius=8,
            command=close_modal
        )
        exit_button.pack(
            pady=(0, 20)
        )

        # Function to update question display
        def update_question_display():
            idx = current_question_index[0]
            if 0 <= idx < len(questions):
                question_data = questions[idx]
                question = question_data["question"]
                answer = question_data["answer"]
                status = self.get_question_status(suspect_id, question_data)
                is_available = status != "LOCKED"

                # Update counter
                counter_label.configure(text=f"QUESTION {idx + 1} OF {len(questions)}  •  {status}")

                if is_available:
                    # Show question
                    question_label.configure(text=question, text_color="#FFFFFF")
                    ask_button.configure(state="normal", fg_color="#1C2C44", text_color="#FFFFFF")

                    # Check if already asked
                    if question_data["id"] in asked_questions:
                        response_label.configure(text=answer, text_color="#D5DCE8")
                        if question_data.get("id") in self.contradictions:
                            present_evidence_button.pack(anchor="w", padx=20, pady=(10, 15))
                            present_evidence_button.configure(command=lambda q=question_data["id"]: self.show_evidence_selection(q, modal))
                        else:
                            present_evidence_button.pack_forget()
                    else:
                        response_label.configure(text="", text_color="#4A5568")
                        present_evidence_button.pack_forget()

                    # Set ask button command
                    ask_button.configure(
                        command=lambda q=question_data, question_number=idx: self.ask_question(
                            suspect_id,
                            question_number,
                            len(questions),
                            q,
                            response_label,
                            counter_label,
                            current_typing,
                            present_evidence_button,
                            modal
                        )
                    )
                else:
                    # Locked question
                    question_label.configure(text="LOCKED — Further investigation required", text_color="#4A5568")
                    ask_button.configure(state="disabled", fg_color="#0F1623", text_color="#4A5568")
                    response_label.configure(text="", text_color="#4A5568")
                    present_evidence_button.pack_forget()

            # Update navigation buttons
            prev_button.configure(state="normal" if current_question_index[0] > 0 else "disabled")
            next_button.configure(state="normal" if current_question_index[0] < len(questions) - 1 else "disabled")

        # Initial display
        update_question_display()

    def type_response(self, label, text, current_typing, btn=None, q_id=None, modal=None, index=0):
        if not label.winfo_exists():
            return
            
        if index == 0:
            label.configure(text="", text_color="#D5DCE8")
            if btn:
                btn.pack_forget()
            
        if index < len(text):
            current_text = label.cget("text")
            label.configure(text=current_text + text[index])
            current_typing["id"] = self.after(20, self.type_response, label, text, current_typing, btn, q_id, modal, index + 1)
        else:
            current_typing["id"] = None
            if btn and q_id in self.contradictions:
                btn.pack(anchor="w", padx=20, pady=(10, 15))
                btn.configure(command=lambda: self.show_evidence_selection(q_id, modal))

    def ask_question(self, suspect_id, question_index, total_questions, question_data, response_label, counter_label, current_typing, btn=None, modal=None):
        self.asked_questions.setdefault(suspect_id, set()).add(question_data["id"])
        counter_label.configure(text=f"QUESTION {question_index + 1} OF {total_questions}  •  ASKED")
        
        if current_typing.get("id"):
            self.after_cancel(current_typing["id"])
            current_typing["id"] = None
            
        self.type_response(response_label, question_data["answer"], current_typing, btn, question_data.get("id"), modal)

    def show_evidence_selection(self, question_id, interview_modal):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evidence")
        all_evidence = cursor.fetchall()
        cursor.close()
        connection.close()

        modal = ctk.CTkFrame(
            self,
            width=500,
            height=500,
            fg_color="#101A2B",
            corner_radius=15,
            border_width=1,
            border_color="#2A3D57"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        
        modal_title = ctk.CTkLabel(
            modal,
            text="PRESENT EVIDENCE",
            font=("Arial", 18, "bold"),
            text_color="#FFFFFF"
        )
        modal_title.pack(pady=(25, 15))

        instruction = ctk.CTkLabel(
            modal,
            text="Select evidence that challenges this statement:",
            font=("Arial", 13),
            text_color="#7D8DA6"
        )
        instruction.pack(pady=(0, 15))
        
        selection_frame = ctk.CTkScrollableFrame(
            modal,
            fg_color="#162235",
            corner_radius=10,
            width=400,
            height=250
        )
        selection_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        for evidence in all_evidence:
            evidence_button = ctk.CTkButton(
                selection_frame,
                text=f"{evidence['title']}  •  {evidence['evidence_type']}",
                font=("Arial", 13),
                fg_color="transparent",
                hover_color="#1C2C44",
                text_color="#D5DCE8",
                anchor="w",
                height=35,
                command=lambda e_id=evidence['id']: self.check_contradiction(question_id, e_id, modal, interview_modal)
            )
            evidence_button.pack(fill="x", padx=15, pady=5)
            
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
        cancel_button.pack(pady=(0, 20))

    def check_contradiction(self, question_id, evidence_id, selection_modal, interview_modal=None):
        selection_modal.destroy()
        
        contradiction = self.contradictions.get(question_id)
        
        if contradiction and contradiction["evidence_id"] == evidence_id:
            deduction_id = contradiction["deduction_id"]
            
            if deduction_id in self.discovered_leads:
                self.show_already_discovered_modal(contradiction["title"])
                return

            unlocked_questions = self.discover_finding(deduction_id)
            widgets_to_close = [interview_modal] if interview_modal else None
            self.show_discovery_modal(deduction_id, widgets_to_close, unlocked_questions)
            
        else:
            result_modal = ctk.CTkFrame(
                self, width=450, height=200, fg_color="#101A2B",
                corner_radius=15, border_width=1, border_color="#2A3D57"
            )
            result_modal.place(relx=0.5, rely=0.5, anchor="center")
            
            title = ctk.CTkLabel(result_modal, text="NO CONTRADICTION FOUND", font=("Arial", 16, "bold"), text_color="#7FA9D8")
            title.pack(pady=(30, 15))
            
            desc = ctk.CTkLabel(result_modal, text="This evidence does not directly challenge the suspect's statement.", font=("Arial", 14), text_color="#7D8DA6")
            desc.pack(pady=(0, 25))
            
            close_btn = ctk.CTkButton(result_modal, text="CONTINUE INTERVIEW", width=180, height=35, fg_color="#1C2C44", hover_color="#2A3D57", text_color="#FFFFFF", command=result_modal.destroy)
            close_btn.pack(pady=(0, 30))
            
    def create_evidence_page(self):
        self.create_page_header(
            "Evidence",
            "Collected evidence connected to CASE #042.",
            "Evidence"
        )

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM evidence")

        evidence_items = cursor.fetchall()

        cursor.close()
        connection.close()

        for evidence in evidence_items:

            evidence_id = evidence["id"]

            card = ctk.CTkFrame(
                self.main_frame,
                fg_color="#162235",
                corner_radius=12,
                border_width=1,
                border_color="#22354E",
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
                pady=(16, 4)
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
                pady=(0, 10)
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
                pady=(0, 10)
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
                pady=(0, 6)
            )

            action_hint = ctk.CTkLabel(
                card,
                text="OPEN EVIDENCE  →",
                font=("Arial", 11, "bold"),
                text_color="#7FA9D8"
            )

            action_hint.pack(
                anchor="e",
                padx=20,
                pady=(0, 14)
            )

            def open_evidence(event, evidence_id=evidence_id):
                self.show_evidence_details(evidence_id)
                return "break"


            widgets = [
                card,
                title_label,
                details_label,
                description_label,
                importance_label,
                action_hint
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

        # Back button
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

        self.create_page_header(
            evidence["title"],
            f'{evidence["evidence_type"]}  •  {evidence["location"]}',
            "Evidence"
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

        # Get current evidence title
        current_evidence = next((e for e in all_evidence if e["id"] == current_evidence_id), None)
        current_evidence_title = current_evidence["title"] if current_evidence else "Unknown"

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
                command=lambda e=evidence, ce=current_evidence_id, cet=current_evidence_title, m=modal: self.show_analysis_modal(e["id"], e["title"], ce, cet, m)
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

    def show_analysis_modal(self, selected_evidence_id, selected_evidence_title, current_evidence_id, current_evidence_title, selection_modal):
        selection_modal.destroy()

        # Create analysis modal (wider for better spacing)
        modal = ctk.CTkFrame(
            self,
            width=600,
            height=580,
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

        # Small blue uppercase header
        header_label = ctk.CTkLabel(
            modal,
            text="ANALYZE CONNECTION",
            font=("Arial", 13, "bold"),
            text_color="#7FA9D8"
        )
        header_label.pack(
            pady=(25, 8)
        )

        # Clear question
        question_label = ctk.CTkLabel(
            modal,
            text="How are these clues connected?",
            font=("Arial", 15),
            text_color="#FFFFFF"
        )
        question_label.pack(
            pady=(0, 20)
        )

        # Evidence display container (horizontal layout)
        evidence_container = ctk.CTkFrame(
            modal,
            fg_color="transparent"
        )
        evidence_container.pack(
            fill="x",
            padx=40,
            pady=(0, 25)
        )

        # First evidence card
        evidence1_card = ctk.CTkFrame(
            evidence_container,
            fg_color="#162235",
            corner_radius=10
        )
        evidence1_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        evidence1_label = ctk.CTkLabel(
            evidence1_card,
            text=current_evidence_title,
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF",
            wraplength=250,
            justify="center"
        )
        evidence1_label.pack(
            padx=15,
            pady=20
        )

        # Connection symbol
        connection_symbol = ctk.CTkLabel(
            evidence_container,
            text="↔",
            font=("Arial", 20, "bold"),
            text_color="#7FA9D8",
            width=30
        )
        connection_symbol.pack(
            side="left",
            padx=5
        )

        # Second evidence card
        evidence2_card = ctk.CTkFrame(
            evidence_container,
            fg_color="#162235",
            corner_radius=10
        )
        evidence2_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0)
        )

        evidence2_label = ctk.CTkLabel(
            evidence2_card,
            text=selected_evidence_title,
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF",
            wraplength=250,
            justify="center"
        )
        evidence2_label.pack(
            padx=15,
            pady=20
        )

        # Connection type section label
        connection_section_label = ctk.CTkLabel(
            modal,
            text="CONNECTION TYPE",
            font=("Arial", 12, "bold"),
            text_color="#7D8DA6"
        )
        connection_section_label.pack(
            pady=(0, 12)
        )

        # Selected connection display
        selected_label = ctk.CTkLabel(
            modal,
            text="",
            font=("Arial", 12),
            text_color="#7FA9D8"
        )
        selected_label.pack(
            pady=(0, 10)
        )

        # Connection type buttons
        connection_types = ["Timeline", "Person", "Location", "Access / System", "Physical Evidence"]
        selected_connection = {"value": None}
        buttons = {}

        for conn_type in connection_types:
            conn_button = ctk.CTkButton(
                modal,
                text=conn_type,
                font=("Arial", 13),
                fg_color="transparent",
                hover_color="#1C2C44",
                text_color="#D5DCE8",
                width=220,
                height=38,
                corner_radius=8,
                command=partial(self.select_connection_type, conn_type, selected_connection, selected_label, buttons)
            )
            conn_button.pack(
                pady=4
            )
            buttons[conn_type] = conn_button

        # Analyze button (primary action)
        analyze_button = ctk.CTkButton(
            modal,
            text="ANALYZE CONNECTION",
            width=200,
            height=42,
            fg_color="#1C2C44",
            hover_color="#2A3D57",
            text_color="#FFFFFF",
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=lambda se=selected_evidence_id, ce=current_evidence_id, sc=selected_connection, m=modal: self.analyze_connection(se, ce, sc["value"], m)
        )
        analyze_button.pack(
            pady=(20, 10)
        )

        # Cancel button
        cancel_button = ctk.CTkButton(
            modal,
            text="CANCEL",
            width=100,
            height=35,
            fg_color="transparent",
            hover_color="#1C2C44",
            text_color="#7D8DA6",
            corner_radius=8,
            command=modal.destroy
        )
        cancel_button.pack(
            pady=(0, 20)
        )

    def select_connection_type(self, connection_type, selected_dict, selected_label, buttons):
        selected_dict["value"] = connection_type
        selected_label.configure(text=f"Selected: {connection_type}", text_color="#7FA9D8")
        
        # Reset all buttons to transparent
        for btn in buttons.values():
            btn.configure(fg_color="transparent", text_color="#D5DCE8")
        
        # Highlight selected button with blue accent
        buttons[connection_type].configure(fg_color="#16345C", text_color="#7FA9D8")

    def analyze_connection(self, selected_evidence_id, current_evidence_id, selected_connection_type, modal):
        if selected_connection_type is None:
            return

        modal.destroy()

        # Check if this is a valid connection
        connection_key = frozenset({current_evidence_id, selected_evidence_id})
        
        if connection_key in self.valid_connections:
            connection_data = self.valid_connections[connection_key]
            
            # Check if already discovered
            if connection_data["id"] in self.discovered_leads:
                self.show_already_discovered_modal(connection_data["title"])
            else:
                # Check if connection type is correct
                if connection_data["connection_type"] == selected_connection_type:
                    # Add to discovered leads
                    unlocked_questions = self.discover_finding(connection_data["id"])
                    self.show_discovery_modal(connection_data["id"], unlocked_questions=unlocked_questions)
                else:
                    # Valid pair but wrong connection type
                    self.show_wrong_connection_type_modal()
        else:
            # Invalid connection
            self.show_invalid_connection_modal()

    def show_wrong_connection_type_modal(self):
        modal = ctk.CTkFrame(
            self,
            width=450,
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
            text="The evidence may be related, but this does not\nappear to be the strongest connection.",
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
        self.create_page_header(
            "Case Findings",
            "Track earned evidence connections, contradictions, and investigation breakthroughs.",
            "Case Findings"
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
                text="No findings documented yet",
                font=("Arial", 18, "bold"),
                text_color="#7D8DA6"
            )

            empty_title.pack(
                pady=(40, 10)
            )

            empty_description = ctk.CTkLabel(
                empty_state_frame,
                text="Analyze evidence, challenge suspect statements, and your discoveries will be recorded here.",
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
            evidence_lookup = self.get_evidence_lookup()

            for finding_id in self.get_discovered_findings():
                finding_data = self.findings_metadata.get(finding_id)
                if not finding_data:
                    continue

                related_evidence = self.get_related_evidence_titles(finding_data, evidence_lookup)

                finding_card = ctk.CTkFrame(
                    self.main_frame,
                    fg_color="#162235",
                    corner_radius=12,
                    border_width=1,
                    border_color="#22354E"
                )

                finding_card.pack(
                    fill="x",
                    padx=40,
                    pady=(0, 15)
                )

                finding_header = ctk.CTkLabel(
                    finding_card,
                    text=self.get_finding_label(finding_data["source_type"]),
                    font=("Arial", 12, "bold"),
                    text_color="#7FA9D8"
                )

                finding_header.pack(
                    anchor="w",
                    padx=20,
                    pady=(18, 10)
                )

                finding_title = ctk.CTkLabel(
                    finding_card,
                    text=finding_data["title"],
                    font=("Arial", 17, "bold"),
                    text_color="#FFFFFF"
                )

                finding_title.pack(
                    anchor="w",
                    padx=20,
                    pady=(0, 10)
                )

                finding_description = ctk.CTkLabel(
                    finding_card,
                    text=finding_data["description"],
                    font=("Arial", 14),
                    text_color="#D5DCE8",
                    justify="left",
                    wraplength=800,
                    anchor="w"
                )

                finding_description.pack(
                    anchor="w",
                    padx=20,
                    pady=(0, 12)
                )

                if related_evidence:
                    evidence_label = ctk.CTkLabel(
                        finding_card,
                        text="RELATED EVIDENCE  •  " + "  +  ".join(related_evidence),
                        font=("Arial", 12, "bold"),
                        text_color="#8B9BB4",
                        justify="left",
                        wraplength=800
                    )

                    evidence_label.pack(
                        anchor="w",
                        padx=20,
                        pady=(0, 18)
                    )

    def create_timeline_page(self):
        self.create_page_header(
            "Timeline",
            "Chronological reconstruction of events.",
            "Timeline"
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
