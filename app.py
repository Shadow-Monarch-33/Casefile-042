import json
import os
import customtkinter as ctk
from database import get_connection
from functools import partial

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

THEMES = {
    "Midnight Blue": {
        "background": "#0A101B",
        "sidebar": "#101A2B",
        "card": "#162235",
        "border": "#2A3D57",
        "primary": "#1C4F82",
        "primary_hover": "#2868A5",
        "accent": "#7FA9D8",
        "heading": "#FFFFFF",
        "text": "#D5DCE8",
        "muted": "#7D8DA6",
        "warning": "#D4A72C",
        "importance_low": "#6B7280",
        "importance_medium": "#D4A72C",
        "importance_high": "#E67E22",
        "importance_critical": "#E74C3C"
    },

    "Crimson Noir": {
        "background": "#120B0E",
        "sidebar": "#1A1014",
        "card": "#24151A",
        "border": "#4A2832",
        "primary": "#7A2638",
        "primary_hover": "#9B3248",
        "accent": "#E89AA8",
        "heading": "#FFFFFF",
        "text": "#E4D7DA",
        "muted": "#A68B91",
        "warning": "#D4A72C",
        "importance_low": "#6B7280",
        "importance_medium": "#D4A72C",
        "importance_high": "#E67E22",
        "importance_critical": "#E74C3C"
    },

    "Emerald Investigation": {
        "background": "#081310",
        "sidebar": "#0E1C18",
        "card": "#142722",
        "border": "#29483F",
        "primary": "#1F6B55",
        "primary_hover": "#2B866C",
        "accent": "#8FD8BE",
        "heading": "#FFFFFF",
        "text": "#D2E5DD",
        "muted": "#819C91",
        "warning": "#D4A72C",
        "importance_low": "#6B7280",
        "importance_medium": "#D4A72C",
        "importance_high": "#E67E22",
        "importance_critical": "#E74C3C"
    },

    "Monochrome": {
        "background": "#111111",
        "sidebar": "#181818",
        "card": "#222222",
        "border": "#3A3A3A",
        "primary": "#555555",
        "primary_hover": "#707070",
        "accent": "#C9C9C9",
        "heading": "#FFFFFF",
        "text": "#DDDDDD",
        "muted": "#999999",
        "warning": "#D4A72C",
        "importance_low": "#6B7280",
        "importance_medium": "#D4A72C",
        "importance_high": "#E67E22",
        "importance_critical": "#E74C3C"
    }
}

class CaseFileApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_page = "case overview"

        self.investigated_evidence = set()
        self.discovered_leads = set()
        self.hints_used = 0
        self.max_hints = 2
        self.shown_hints = set()

        self.discovery_history = []
        self.asked_questions = {}
        self.active_reaction = None
        self.nav_button_rows = {}
        self.nav_buttons = {}
        self.nav_badges = {}
        self.pending_timeline_focus = None
        self.timeline_event_widgets = {}
        self.case_closed = False
        self.resolution_unlocked = False

        self.current_theme = self.load_settings()

        self.theme = THEMES[
            self.current_theme
        ]

        self.page_config = {
            "case overview": {"label": "Case Overview", "icon": "▣"},
            "suspects": {"label": "Suspects", "icon": "◉"},
            "evidence": {"label": "Evidence", "icon": "⌕"},
            "timeline": {"label": "Timeline", "icon": "◷"},
            "deduction board": {"label": "Case Findings", "icon": "✦"},
            "settings": {"label": "Settings", "icon": "⚙"},
            "case resolution": {"label": "Case Resolution", "icon": "◈"}
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
            },
            frozenset({1, 5}): {
                "id": "elena_murder_window",
                "title": "ELENA INSIDE THE MURDER WINDOW",
                "description": (
                    "Elena's card was used on the executive floor only minutes "
                    "before the victim's watch stopped at 10:24 PM."
                ),
                "evidence_ids": {1, 5},
                "connection_type": "Timeline"
            },
            frozenset({1, 7}): {
                "id": "coordinated_access_window",
                "title": "COORDINATED ACCESS WINDOW",
                "description": (
                    "The security administrator login and Elena's badge use happened "
                    "within minutes of each other, suggesting a coordinated breach."
                ),
                "evidence_ids": {1, 7},
                "connection_type": "Access / System"
            },
            frozenset({2, 6}): {
                "id": "marcus_financial_pressure",
                "title": "MARCUS UNDER FINANCIAL PRESSURE",
                "description": (
                    "Marcus's failed investor meeting and deleted records point to a "
                    "financial motive he was trying to hide."
                ),
                "evidence_ids": {2, 6},
                "connection_type": "Person"
            },
            frozenset({2, 5}): {
                "id": "financial_coverup_window",
                "title": "FINANCIAL COVER-UP DURING THE CASE WINDOW",
                "description": (
                    "The deleted records gain weight when placed against the victim's "
                    "struggle window, suggesting Marcus was cleaning up under pressure."
                ),
                "evidence_ids": {2, 5},
                "connection_type": "Timeline"
            },
            frozenset({3, 5}): {
                "id": "noah_confirmed_elsewhere",
                "title": "NOAH CONFIRMED ELSEWHERE",
                "description": (
                    "The server room footage overlaps the struggle window, narrowing "
                    "Noah's opportunity during the murder itself."
                ),
                "evidence_ids": {3, 5},
                "connection_type": "Timeline"
            },
            frozenset({4, 5}): {
                "id": "blackout_during_struggle",
                "title": "BLACKOUT DURING THE STRUGGLE",
                "description": (
                    "The estimated struggle happened while the executive floor cameras "
                    "were dark, giving the killer a concealed window."
                ),
                "evidence_ids": {4, 5},
                "connection_type": "Timeline"
            },
            frozenset({7, 8}): {
                "id": "sophie_security_overlap",
                "title": "SOPHIE TIED TO SYSTEMS AND SCENE",
                "description": (
                    "Sophie's security-admin link and lipstick trace place her "
                    "close to both the blackout systems and the victim's office."
                ),
                "evidence_ids": {7, 8},
                "connection_type": "Person"
            },
            frozenset({1, 8}): {
                "id": "elena_sophie_same_floor",
                "title": "TWO PEOPLE ON THE EXECUTIVE FLOOR",
                "description": (
                    "Elena's access activity and Sophie's trace inside the victim's office "
                    "suggest that more than one person may have been connected to the "
                    "executive floor that night."
                ),
                "evidence_ids": {1, 8},
                "connection_type": "Person"
            },

            frozenset({2, 7}): {
                "id": "financial_access_to_security",
                "title": "FINANCIAL PRESSURE AND SYSTEM ACCESS",
                "description": (
                    "The deleted financial records establish a possible motive, while the "
                    "security administrator activity raises the possibility that someone "
                    "may have tried to control what could be seen or recorded."
                ),
                "evidence_ids": {2, 7},
                "connection_type": "Motive / System"
            },
            frozenset({3, 4}): {
                "id": "selective_camera_failure",
                "title": "SELECTIVE CAMERA BLACKOUT",
                "description": (
                    "The server room camera continued recording while the executive floor "
                    "cameras went offline, suggesting the blackout was selective rather "
                    "than a building-wide system failure."
                ),
                "evidence_ids": {3, 4},
                "connection_type": "System"
            },
            frozenset({3, 7}): {
                "id": "security_systems_intact",
                "title": "SECURITY SYSTEMS WERE STILL ACTIVE",
                "description": (
                    "The continued server room recording alongside the security administrator "
                    "login suggests the wider surveillance system remained functional while "
                    "only the executive floor lost visibility."
                ),
                "evidence_ids": {3, 7},
                "connection_type": "System"
            },
            frozenset({5, 8}): {
                "id": "sophie_near_critical_window",
                "title": "SOPHIE CONNECTED TO THE CRITICAL PERIOD",
                "description": (
                    "The victim's watch places the estimated struggle at 10:24 PM, while "
                    "Sophie's trace establishes that she had been inside the victim's office "
                    "that night, making her movements during the critical period important."
                ),
                "evidence_ids": {5, 8},
                "connection_type": "Timeline"
            },
            frozenset({6, 7}): {
                "id": "marcus_opportunity_blackout",
                "title": "UNACCOUNTED FOR DURING SECURITY ACTIVITY",
                "description": (
                    "Marcus's meeting ended before the critical struggle window, while "
                    "security administrator activity occurred shortly afterwards, leaving "
                    "important movements during the blackout unexplained."
                ),
                "evidence_ids": {6, 7},
                "connection_type": "Timeline"
            },
            frozenset({2, 8}): {
                "id": "motive_and_scene_presence",
                "title": "MOTIVE AND SCENE CONNECTION",
                "description": (
                    "The financial records point toward a possible motive, while the "
                    "physical trace in the victim's office shows that the investigation "
                    "must distinguish between motive and actual presence."
                ),
                "evidence_ids": {2, 8},
                "connection_type": "Motive / Person"
            },
            frozenset({1, 6}): {
                "id": "multiple_unverified_accounts",
                "title": "MULTIPLE ACCOUNTS UNDER QUESTION",
                "description": (
                    "Elena's recorded access and Marcus's shortened meeting both conflict "
                    "with their initial accounts, revealing that more than one suspect may "
                    "be concealing part of their movements."
                ),
                "evidence_ids": {1, 6},
                "connection_type": "Person"
            },
            frozenset({7, 9}): {
                "id": "sophie_security_workstation",
                "title": "SECURITY SESSION ORIGIN",
                "description": (
                    "The administrator session responsible for the security blackout "
                    "originated from workstation SEC-03, assigned to Sophie Laurent."
                ),
                "evidence_ids": {7, 9},
                "connection_type": "Access / System"
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
                },
                {
                    "id": "elena_q4",
                    "question": "Your badge was used minutes before the struggle. Why were you still on that floor?",
                    "answer": "I wasn't still there. If my badge appeared that close to the struggle, someone wanted it to look that way.",
                    "requires": "elena_murder_window"
                },
                {
                    "id": "elena_q5",
                    "question": "Who could pair a badge swipe with a security blackout that precisely?",
                    "answer": "Someone with access to the security systems, or someone Sophie trusted enough to leave near her desk. That timing wasn't luck.",
                    "requires": "coordinated_access_window"
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
                    "question": "Were you deleting financial records while the case was unfolding?",
                    "answer": "No. I did not touch the finance server that night. I had bigger problems than bookkeeping.",
                    "requires": "marcus_financial_pressure"
                },
                {
                    "id": "marcus_q5",
                    "question": "If the records mattered enough to erase, what exactly were you hiding from Victor?",
                    "answer": "He found transfers I couldn't explain away. If the board saw them before I fixed the mess, I was finished.",
                    "requires": ["marcus_financial_coverup", "marcus_unverified_window"]
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
                },
                {
                    "id": "noah_q3",
                    "question": "What does the blackout change about the timeline from your perspective?",
                    "answer": "It means the executive floor went blind exactly when the struggle likely happened. My camera stayed up, theirs didn't.",
                    "requires": "blackout_during_struggle"
                },
                {
                    "id": "noah_q4",
                    "question": "Could someone have tampered with the footage that keeps you in the server room?",
                    "answer": "Not without hitting the isolated backup too. That recorder mirrors off-site, which is why I knew my timeline would hold.",
                    "requires": "noah_confirmed_elsewhere"
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
                },
                {
                    "id": "sophie_q5",
                    "question": "Why did you say the systems looked normal if the blackout had already started?",
                    "answer": "Because admitting I missed a manual override would have made security look compromised before I knew how bad it was.",
                    "requires": "sophie_systems_lie"
                },
                {
                    "id": "sophie_q6",
                    "question": "How did your security access and your trace in the office surface on the same night?",
                    "answer": "I had reason to be near both. That doesn't make me the one who used the blackout window.",
                    "requires": "sophie_security_overlap"
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
            },
            "sophie_q2": {
                "evidence_id": 4,
                "deduction_id": "sophie_systems_lie",
                "title": "SOPHIE'S FALSE SYSTEM CHECK",
                "description": "Sophie says the security systems looked normal, but the executive floor cameras were manually blacked out from 10:10 PM to 10:28 PM."
            },
            "marcus_q4": {
                "evidence_id": 2,
                "deduction_id": "marcus_financial_coverup",
                "title": "MARCUS ERASED THE TRAIL",
                "description": "Marcus denies touching the finance server, but deleted financial records were tied directly to his activity before the murder."
            }
        }

        self.presented_evidence_reactions = {
            1: {
                "elena_q2": {
                    1: {"reaction": "Elena's jaw tightens. 'That only proves my badge was used. It does not prove I was the one carrying it.'", "result": "contradiction"},
                    4: {"reaction": "Elena folds her arms. 'A blackout does not put me on that floor. You're still missing the person behind it.'", "result": "suspicious"},
                    5: {"reaction": "She glances at the watch and exhales. 'A time of struggle is not the same thing as proof I was there.'", "result": "suspicious"},
                    7: {"reaction": "Her eyes flick to the side. 'If admin credentials were involved, security had more control over that floor than I did.'", "result": "suspicious"}
                },
                "elena_q3": {
                    1: {"reaction": "Elena rubs her temple. 'You're showing me the same badge log again. I am telling you the card was compromised.'", "result": "suspicious"},
                    4: {"reaction": "'Exactly,' Elena says. 'Whoever did this made sure the cameras were dark before my badge appeared.'", "result": "suspicious"},
                    7: {"reaction": "She leans forward. 'That security login matters more than my badge. Someone with system access opened the window first.'", "result": "suspicious"}
                }
            },
            2: {
                "marcus_q1": {
                    6: {"reaction": "Marcus stops talking mid-breath. 'The meeting ended early, yes, but that does not make me a killer.'", "result": "contradiction"},
                    5: {"reaction": "He straightens his tie. 'A broken watch gives you a time, not my location.'", "result": "suspicious"},
                    2: {"reaction": "Marcus's expression hardens. 'Those records have nothing to do with where I was during the meeting.'", "result": "suspicious"}
                },
                "marcus_q3": {
                    2: {"reaction": "His mouth tightens. 'Financial pressure is not the same as murder. Do not pretend it is.'", "result": "suspicious"},
                    5: {"reaction": "Marcus looks away for a moment. 'You are trying to turn a bad night into a confession.'", "result": "suspicious"}
                },
                "marcus_q4": {
                    2: {"reaction": "Marcus goes silent, then forces a smile. 'Those records were supposed to be gone. Fine. I touched the finance server, but that still doesn't place me in Victor's office.'", "result": "contradiction"},
                    5: {"reaction": "He taps the table once. 'That only tells you when the struggle happened, not what I was doing.'", "result": "suspicious"},
                    6: {"reaction": "Marcus bristles. 'I already admitted the meeting ended early. That isn't the same as saying I touched those records.'", "result": "suspicious"}
                }
            },
            4: {
                "sophie_q1": {
                    8: {"reaction": "Sophie's composure slips. 'That cup should not have still been there. I told you I was only in the office earlier.'", "result": "contradiction"},
                    4: {"reaction": "She narrows her eyes. 'A blackout in the system does not tell you where I was standing.'", "result": "suspicious"},
                    7: {"reaction": "Sophie answers too quickly. 'Admin credentials were used, yes. That still doesn't mean I left the security office.'", "result": "suspicious"}
                },
                "sophie_q2": {
                    4: {"reaction": "Sophie stiffens. 'That override was logged? Then I should have caught it sooner.'", "result": "contradiction"},
                    7: {"reaction": "She looks annoyed. 'An admin login means someone had console access. It does not prove I saw the override happen.'", "result": "suspicious"},
                    8: {"reaction": "Sophie frowns. 'That coffee cup has nothing to do with whether the monitors looked normal.'", "result": "irrelevant"}
                },
                "sophie_q4": {
                    7: {"reaction": "Sophie squares her shoulders. 'That login is exactly why I'm telling you an active admin session was involved.'", "result": "suspicious"},
                    4: {"reaction": "'You already know the blackout happened,' Sophie says. 'What you still don't know is who was at the terminal.'", "result": "suspicious"}
                }
            }
        }

        self.timeline_events = self.build_timeline_events()

        self.additional_findings = {}
        self.findings_metadata = {}
        self.rebuild_findings_metadata()

        # Case Resolution Configuration
        self.resolution_config = {
            "unlock_conditions": {
                "required_findings": [
                    "security_override_access",  # Sophie had admin access
                    "sophie_security_overlap",  # Sophie tied to systems and scene
                    "sophie_systems_lie",  # Sophie lied about systems
                    "blackout_during_struggle"  # Timeline coordination
                ],
                "required_contradictions": [
                    "sophie_systems_lie",
                    "sophie_office_presence"
                ]
            },
            "correct_solution": {
                "suspect_id": 4,  # Sophie Laurent
                "critical_timeline": {
                    "start": "10:10 PM",
                    "end": "10:28 PM",
                    "event": "Security blackout and executive floor access"
                },
                "method": "Used security administrator credentials to disable cameras, then used Elena's access card to access executive floor",
                "motive": "Her lipstick and security logs would expose her presence and system manipulation",
                "supporting_evidence_ids": [4, 7, 8, 9],  # Security camera gap, Security console login, Coffee cup
                "required_evidence_count": 3,
                "required_timeline_events": [
                    "executive_blackout",
                    "elena_badge_access",
                    "sophie_systems_and_scene"
                ]
            }
        }

        self.title("CASEFILE")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.create_layout()
        self.update_case_progress()

        self.show_page("case overview")

        self.after(150, self.show_case_briefing)

    def create_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=self.theme["sidebar"]
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
            text_color=self.theme["heading"]
        )

        self.logo_label.pack(
            pady=(40, 5)
        )


        # Case number
        self.case_label = ctk.CTkLabel(
            self.sidebar,
            text="CASE #042",
            font=("Arial", 13),
            text_color=self.theme["accent"]
        )

        self.case_label.pack(
            pady=(0, 30)
        )

        self.build_sidebar_navigation()

        # Main Area
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color=self.theme["background"]
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

        elif page_name == "settings":
            self.show_settings_page()

        elif page_name == "case resolution":
            self.show_case_resolution_page()

    def show_case_briefing(self, revisit=False):

        # Dark overlay
        overlay = ctk.CTkFrame(
            self,
            fg_color=self.theme["background"],
            corner_radius=0
        )

        overlay.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        # Main briefing container
        briefing = ctk.CTkFrame(
            overlay,
            width=760,
            height=600,
            fg_color=self.theme["card"],
            corner_radius=18,
            border_width=1,
            border_color=self.theme["border"]
        )

        briefing.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        briefing.pack_propagate(False)

        # CASEFILE label
        casefile_label = ctk.CTkLabel(
            briefing,
            text="CASEFILE",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        )

        casefile_label.pack(
            pady=(35, 4)
        )

        # Case number
        case_number = ctk.CTkLabel(
            briefing,
            text="CASE #042",
            font=("Arial", 28, "bold"),
            text_color=self.theme["heading"]
        )

        case_number.pack()

        # Divider
        divider = ctk.CTkFrame(
            briefing,
            height=1,
            fg_color=self.theme["border"]
        )

        divider.pack(
            fill="x",
            padx=50,
            pady=(20, 20)
        )

        # Section
        briefing_label = ctk.CTkLabel(
            briefing,
            text="INITIAL BRIEFING",
            font=("Arial", 12, "bold"),
            text_color=self.theme["warning"]
        )

        briefing_label.pack()

        # Main briefing text
        briefing_text = ctk.CTkLabel(
            briefing,
            text="",
            font=("Arial", 14),
            text_color=self.theme["text"],
            justify="center",
            wraplength=620
        )

        briefing_text.pack(
            padx=60,
            pady=(12, 20)
        )

        # Briefing Content

        briefing_pages = [
            {
                "heading": "THE INCIDENT",
                "heading_color": self.theme["warning"],
                "text": (
                    "At approximately 11:05 PM, a member of staff was found dead "
                    "inside an office on the executive floor.\n\n"

                    "The circumstances surrounding the death are unclear.\n\n"

                    "The events leading up to the discovery have not yet been fully "
                    "reconstructed, and the available evidence does not provide a "
                    "complete explanation on its own.\n\n"

                    "Your investigation begins with one question:\n\n"

                    "What happened before 11:05 PM?"
                )
            },
            {
                "heading": "THE CRITICAL WINDOW",
                "heading_color": self.theme["accent"],
                "text": (
                    "Investigators have identified the period between 10:00 PM and "
                    "11:05 PM as the most important unresolved period of the case.\n\n"

                    "What happened during this window is not yet known.\n\n"

                    "The available records may contain fragments of the truth, but "
                    "they have not yet been assembled into a reliable sequence of "
                    "events.\n\n"

                    "Your task is to determine how the events of that night connect "
                    "and reconstruct what happened during the missing period."
                )
            },
            {
                "heading": "THE PEOPLE INVOLVED",
                "heading_color": self.theme["accent"],
                "text": (
                    "Four individuals are currently connected to the investigation.\n\n"

                    "Each may possess information relevant to the events of that "
                    "night.\n\n"

                    "Their statements should not automatically be accepted as fact.\n\n"

                    "As new evidence is discovered, you may uncover inconsistencies "
                    "between what a suspect claims and what the records actually show.\n\n"

                    "Question them carefully. What someone says may be important — "
                    "but so may what they cannot explain."
                )
            },
            {
                "heading": "INITIAL CASE MATERIAL",
                "heading_color": self.theme["accent"],
                "text": (
                    "Your investigation begins with access to the evidence collected "
                    "from the case.\n\n"

                    "Examine each piece carefully.\n\n"

                    "A single record may appear insignificant when viewed alone, but "
                    "its meaning can change when compared with another piece of "
                    "information.\n\n"

                    "Pay close attention to timing, locations, actions, and any details "
                    "that appear to contradict another account.\n\n"

                    "The answers may not be contained in one piece of evidence."
                )
            },
            {
                "heading": "HOW TO INVESTIGATE",
                "heading_color": self.theme["accent"],
                "text": (
                    "Examine the available evidence and look for meaningful "
                    "relationships between different records.\n\n"

                    "When two pieces of evidence appear connected, analyze their "
                    "relationship to uncover new findings.\n\n"

                    "New discoveries may reveal additional information, update the "
                    "timeline, or provide new directions for questioning a suspect.\n\n"

                    "Build your understanding of the case gradually.\n\n"

                    "Do not guess. Follow what the evidence can actually support."
                )
            },
            {
                "heading": "YOUR OBJECTIVE",
                "heading_color": self.theme["accent"],
                "text": (
                    "Examine the evidence.\n\n"

                    "Identify meaningful connections.\n\n"

                    "Reconstruct the events of the critical window.\n\n"

                    "Question the individuals connected to the investigation.\n\n"

                    "Challenge statements that conflict with the evidence.\n\n"

                    "Build the case one discovery at a time.\n\n"

                    "The truth is already somewhere in the case file.\n\n"

                    "Your job is to find it."
                )
            }
        ]

        # Reuse the existing labels

        current_page = 0


        def show_briefing_page():

            page = briefing_pages[current_page]

            # Reset text
            briefing_label.configure(
                text=page["heading"],
                text_color=page["heading_color"]
            )

            briefing_text.configure(
                text=""
            )

            next_button.pack_forget()

            # Type page text
            def type_text(index=0):

                if index < len(page["text"]):

                    briefing_text.configure(
                        text=page["text"][:index + 1]
                    )

                    briefing.after(
                        20,
                        lambda: type_text(index + 1)
                    )

                else:

                    briefing.after(
                        400,
                        show_next_button
                    )

            type_text()


        def show_next_button():

            # Last page → Begin Investigation
            if current_page == len(briefing_pages) - 1:

                next_button.configure(
                    text="RETURN TO CASE  →" if revisit else "BEGIN INVESTIGATION  →",
                    command=overlay.destroy
                )

            # Normal page → Next
            else:

                next_button.configure(
                    text="NEXT  →",
                    command=next_page
                )

            next_button.pack(
                pady=(30, 30)
            )


        def next_page():

            nonlocal current_page

            current_page += 1

            show_briefing_page()


        # Button

        next_button = ctk.CTkButton(
            briefing,
            text="",
            width=240,
            height=44,
            font=("Arial", 14, "bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"]
        )


        # Start first page

        show_briefing_page()

    def build_sidebar_navigation(self):
        nav_items = [
            "case overview",
            "suspects",
            "evidence",
            "timeline",
            "deduction board",
            "case resolution",
            "settings"
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
                hover_color=self.theme["primary"],
                text_color=self.theme["text"],
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
                fg_color=self.theme["card"],
                text_color=self.theme["accent"]
            )
            if page_name in ("deduction board", "timeline"):
                badge.pack(side="right", padx=(0, 6))
                if page_name == "deduction board":
                    self.deduction_board_button = button

            self.nav_button_rows[page_name] = row
            self.nav_buttons[page_name] = button
            self.nav_badges[page_name] = badge

        # Push utility buttons to the bottom
        bottom_spacer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        bottom_spacer.pack(fill="both", expand=True)


        briefing_button = ctk.CTkButton(
            self.sidebar,
            text="📁  CASE BRIEFING",
            font=("Arial", 13, "bold"),
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["text"],
            command=self.show_case_briefing
        )

        briefing_button.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        # Hint Button
        self.hint_button = ctk.CTkButton(
            self.sidebar,
            text="💡  HINTS  (2)",
            font=("Arial", 13, "bold"),
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["text"],
            command=self.show_hint
        )

        self.hint_button.pack(
            fill="x",
            padx=15,
            pady=(0, 20)
        )

    def get_contextual_hint(self):

        evidence_count = len(self.investigated_evidence)
        leads = self.discovered_leads


        # ─────────────────────────────────────
        # Very Early Game
        # ─────────────────────────────────────

        if evidence_count == 0:
            return (
                "Every investigation starts with the evidence. Begin by examining "
                "the records and objects connected to the night of the incident."
            )

        if evidence_count < 3:
            return (
                "Several important events occurred within a narrow time window. "
                "Pay close attention to what happened between 10:10 PM and 10:28 PM."
            )


        # ─────────────────────────────────────
        # Blackout / Security Access
        # ─────────────────────────────────────

        if "security_override_access" not in leads:
            return (
                "The CCTV blackout was manually triggered. Compare the camera "
                "records with evidence that explains how the security system "
                "was accessed."
            )

        if "sophie_security_workstation" not in leads:
            return (
                "Knowing that a security administrator account was used is only "
                "part of the story. Try to determine where that session originated."
            )


        # ─────────────────────────────────────
        # Elena / Access Card
        # ─────────────────────────────────────

        if "access_during_blackout" not in leads:
            return (
                "Elena's access card was used at 10:12 PM. The timing may be more "
                "important than the identity printed on the card."
            )


        # ─────────────────────────────────────
        # Marcus
        # ─────────────────────────────────────

        if evidence_count < 6:
            return (
                "An alibi is only useful if it covers the right period of time. "
                "Look closely at when Marcus's meeting actually ended."
            )


        # ─────────────────────────────────────
        # Noah
        # ─────────────────────────────────────

        if evidence_count < 8:
            return (
                "Being suspicious is not the same as having the opportunity to "
                "commit the crime. Compare Noah's confirmed location with the "
                "estimated time of the struggle."
            )


        # ─────────────────────────────────────
        # Sophie's connection to the office
        # ─────────────────────────────────────

        if "sophie_office_presence" not in leads:
            return (
                "Someone's presence near the victim does not automatically prove "
                "guilt. But it can become important when combined with other "
                "events from the same time period."
            )


        # ─────────────────────────────────────
        # Player has many clues but is stuck
        # ─────────────────────────────────────

        if len(leads) < 4:
            return (
                "Try connecting evidence that appears to describe different parts "
                "of the same event. Time, location, and access are often more "
                "useful together than separately."
            )

        if len(leads) < 6:
            return (
                "Not every suspicious person is equally important. Ask yourself "
                "which suspect is connected to the greatest number of critical "
                "events surrounding the estimated time of the murder."
            )


        # ─────────────────────────────────────
        # Late game
        # ─────────────────────────────────────

        if len(leads) < 8:
            return (
                "The strongest theory should not merely identify someone with a "
                "motive. It should also explain how that person had the opportunity "
                "to act without being observed."
            )


        # ─────────────────────────────────────
        # Final fallback
        # ─────────────────────────────────────

        return (
            "Look for one explanation that connects the blackout, the executive "
            "floor activity, the estimated time of the struggle, and the "
            "contradictions in the suspects' accounts."
        )

    def show_hint(self):

        # No hints remaining
        if self.hints_used >= self.max_hints:

            dialog = ctk.CTkToplevel(self)

            dialog.title("Hints")

            dialog.geometry("420x230")

            dialog.configure(
                fg_color=self.theme["background"]
            )

            dialog.transient(self)

            dialog.grab_set()

            title = ctk.CTkLabel(
                dialog,
                text="NO HINTS REMAINING",
                font=("Arial", 18, "bold"),
                text_color=self.theme["accent"]
            )

            title.pack(
                pady=(35, 10)
            )

            message = ctk.CTkLabel(
                dialog,
                text=(
                    "You have used both available hints.\n\n"
                    "The remaining connections are yours to uncover."
                ),
                font=("Arial", 13),
                text_color=self.theme["text"],
                justify="center",
                wraplength=330
            )

            message.pack(
                padx=30,
                pady=(0, 20)
            )

            close_button = ctk.CTkButton(
                dialog,
                text="RETURN TO CASE",
                width=180,
                height=38,
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                text_color=self.theme["heading"],
                command=dialog.destroy
            )

            close_button.pack()

            return


        # Get the best hint for current progress
        hint = self.get_contextual_hint()

        # Only consume a hint if this is a new hint
        is_new_hint = hint not in self.shown_hints

        if is_new_hint:
            self.shown_hints.add(hint)
            self.hints_used += 1

        remaining = self.max_hints - self.hints_used


        # Hint window
        dialog = ctk.CTkToplevel(self)

        dialog.title("Investigation Hint")

        dialog.geometry("520x320")

        dialog.configure(
            fg_color=self.theme["background"]
        )

        dialog.transient(self)

        dialog.grab_set()


        title = ctk.CTkLabel(
            dialog,
            text=(
                f"💡 INVESTIGATION HINT  {self.hints_used}/2"
                if is_new_hint
                else f"💡 PREVIOUS HINT  •  {self.hints_used}/2 USED"
            ),
            font=("Arial", 18, "bold"),
            text_color=self.theme["accent"]
        )

        title.pack(
            pady=(35, 15)
        )


        divider = ctk.CTkFrame(
            dialog,
            height=1,
            fg_color=self.theme["border"]
        )

        divider.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )


        hint_label = ctk.CTkLabel(
            dialog,
            text=hint,
            font=("Arial", 14),
            text_color=self.theme["text"],
            justify="center",
            wraplength=420
        )

        hint_label.pack(
            padx=40,
            pady=(0, 20)
        )


        remaining_label = ctk.CTkLabel(
            dialog,
            text=(
                f"{remaining} HINT REMAINING"
                if remaining == 1
                else f"{remaining} HINTS REMAINING"
            ),
            font=("Arial", 11, "bold"),
            text_color=self.theme["muted"]
        )

        remaining_label.pack(
            pady=(0, 15)
        )


        close_button = ctk.CTkButton(
            dialog,
            text="CONTINUE INVESTIGATION",
            width=210,
            height=38,
            font=("Arial", 12, "bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"],
            command=dialog.destroy
        )

        close_button.pack(
            pady=(0, 25)
        )


        # Update the sidebar hint button
        if remaining > 0:

            self.hint_button.configure(
                text=f"💡  HINTS  ({remaining})"
            )

        else:

            self.hint_button.configure(
                text="💡  HINTS USED",
                state="disabled",
                text_color=self.theme["muted"]
            )

    def update_nav_state(self):

        for page_name, button in self.nav_buttons.items():

            is_active = (
                page_name == self.current_page
            )

            self.nav_button_rows[page_name].configure(
                fg_color=(
                    self.theme["primary"]
                    if is_active
                    else "transparent"
                ),
                border_color=(
                    self.theme["accent"]
                    if is_active
                    else self.theme["border"]
                )
            )

            button.configure(
                fg_color=(
                    self.theme["primary"]
                    if is_active
                    else "transparent"
                ),
                text_color=(
                    self.theme["heading"]
                    if is_active
                    else self.theme["text"]
                ),
                hover_color=self.theme["primary_hover"]
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

        if "deduction board" in self.nav_badges:

            findings_count = len(self.discovered_leads)

            badge = self.nav_badges["deduction board"]

            if findings_count:

                badge.configure(
                    text=str(findings_count),
                    fg_color=self.theme["card"],
                    text_color=self.theme["heading"]
                )

                badge.pack(
                    side="right",
                    padx=(0, 6)
                )

            else:

                badge.pack_forget()


        if "timeline" in self.nav_badges:

            discovered, total = self.get_timeline_progress()

            timeline_badge = self.nav_badges["timeline"]

            if discovered:

                timeline_badge.configure(
                    text=str(discovered),
                    fg_color=self.theme["card"],
                    text_color=self.theme["heading"]
                )

                timeline_badge.pack(
                    side="right",
                    padx=(0, 6)
                )

            else:

                timeline_badge.pack_forget()

    def discover_finding(self, finding_id):
        empty = {"questions": [], "timeline_new": [], "timeline_updated": []}
        if finding_id in self.discovered_leads:
            return empty

        before_events = {
            item["id"]: (item["title"], item["description"])
            for item in self.get_resolved_timeline_events()
        }

        self.discovered_leads.add(finding_id)
        self.discovery_history.append(finding_id)
        self.update_case_progress()

        # Check if case resolution should be unlocked
        self.check_resolution_unlock()

        return {
            "questions": self.get_newly_unlocked_questions(finding_id),
            **self.diff_timeline_state(before_events)
        }

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

    def build_timeline_events(self):
        return [
            {
                "id": "victim_discovered",
                "sort_key": "23:05:00",
                "time": "11:05 PM",
                "title": "Victim Discovered",
                "description": (
                    "The victim is found dead inside his office on the executive floor. "
                    "This is the known start of the investigation."
                ),
                "location": "Victim's Office",
                "event_type": "SCENE",
                "unlocked_by": None
            },
            {
                "id": "gap_evening",
                "kind": "gap",
                "sort_key": "21:50:00",
                "time": "10:00 PM – 11:05 PM",
                "title": "Investigation Gap",
                "description": "Further evidence may clarify what happened during this period.",
                "unlocked_by": None,
                "hidden_when_any": [
                    "elena_claimed_exit",
                    "sophie_office_visit",
                    "noah_enters_server",
                    "marcus_meeting_ends",
                    "executive_blackout",
                    "elena_badge_access",
                    "struggle"
                ]
            },
            {
                "id": "elena_claimed_exit",
                "sort_key": "21:40:00",
                "time": "9:40 PM",
                "title": "Elena Claims She Left",
                "description": (
                    "Elena says she left the executive floor around 9:40 PM and went home. "
                    "This remains her stated account, not yet independently confirmed."
                ),
                "location": "Executive Floor",
                "event_type": "WITNESS",
                "unlocked_by": {"any": ["elena_q1", "elena_access_lie"]},
                "clarifications": [
                    {
                        "when": "elena_access_lie",
                        "title": "Elena's Departure Claim Breaks",
                        "description": (
                            "Elena still claims she left before 10 PM, but her access card "
                            "was used on the executive floor at 10:12 PM."
                        ),
                        "event_type": "DEDUCTION"
                    }
                ]
            },
            {
                "id": "sophie_office_visit",
                "sort_key": "21:30:00",
                "time": "Earlier that evening",
                "title": "Sophie Linked to the Victim's Office",
                "description": (
                    "Sophie's lipstick was found on a coffee cup in the victim's office, "
                    "placing her in that room at some point despite her security-office alibi."
                ),
                "location": "Victim's Office",
                "event_type": "WITNESS",
                "unlocked_by": "sophie_office_presence",
                "clarifications": [
                    {
                        "when": "sophie_q3",
                        "time": "9:30 PM",
                        "title": "Sophie in the Office Around 9:30 PM",
                        "description": (
                            "Sophie admits she was in the victim's office around 9:30 PM "
                            "to discuss access log audits, and says the cup was left from that visit."
                        )
                    }
                ]
            },
            {
                "id": "noah_enters_server",
                "sort_key": "22:05:00",
                "time": "10:05 PM",
                "title": "Noah Enters the Server Room",
                "description": (
                    "Server-room CCTV places Noah Bennett inside from 10:05 PM, "
                    "overlapping the estimated struggle window."
                ),
                "location": "Server Room",
                "event_type": "SYSTEM",
                "unlocked_by": "noah_confirmed_elsewhere"
            },
            {
                "id": "marcus_meeting_ends",
                "sort_key": "22:08:00",
                "time": "10:08 PM",
                "title": "Investor Meeting Ends",
                "description": (
                    "Marcus's investor meeting ended before the 10:24 PM struggle, "
                    "leaving his movements unverified during a critical window."
                ),
                "location": "Conference Room",
                "event_type": "ACCESS",
                "unlocked_by": {"any": ["marcus_unverified_window", "marcus_meeting_lie"]},
                "clarifications": [
                    {
                        "when": "marcus_meeting_lie",
                        "title": "Meeting Ended at 10:08 PM",
                        "description": (
                            "Records show the investor meeting ended at 10:08 PM, "
                            "contradicting Marcus's claim that it continued until 10:30 PM."
                        ),
                        "event_type": "DEDUCTION"
                    }
                ]
            },
            {
                "id": "marcus_unverified",
                "sort_key": "22:08:30",
                "time": "10:08 PM – 10:24 PM",
                "title": "Marcus Unaccounted For",
                "description": (
                    "After the meeting ended, Marcus's whereabouts are unverified "
                    "through the estimated time of the struggle."
                ),
                "location": "Unknown",
                "event_type": "DEDUCTION",
                "unlocked_by": "marcus_unverified_window",
                "clarifications": [
                    {
                        "when": "marcus_q3",
                        "title": "Marcus Walking the Building",
                        "description": (
                            "Marcus admits the meeting ended early and says he was walking "
                            "around the building to clear his head, still denying the executive floor."
                        ),
                        "event_type": "WITNESS"
                    }
                ]
            },
            {
                "id": "financial_records_deleted",
                "sort_key": "22:00:00",
                "time": "Shortly before the murder",
                "title": "Financial Records Deleted",
                "description": (
                    "Transaction records connected to Marcus were deleted shortly before "
                    "the murder, pointing to financial pressure he was trying to hide."
                ),
                "location": "Finance Server",
                "event_type": "SYSTEM",
                "unlocked_by": {"any": ["marcus_financial_pressure", "marcus_financial_coverup", "financial_coverup_window"]},
                "clarifications": [
                    {
                        "when": "financial_coverup_window",
                        "title": "Cleanup During the Case Window",
                        "description": (
                            "The deleted records gain weight against the 10:24 PM struggle window, "
                            "suggesting Marcus was cleaning up under pressure as the case unfolded."
                        )
                    },
                    {
                        "when": "marcus_financial_coverup",
                        "title": "Marcus Erased the Trail",
                        "description": (
                            "Marcus denied touching the finance server, but the deleted records "
                            "were tied directly to his activity before the murder."
                        ),
                        "event_type": "DEDUCTION"
                    }
                ]
            },
            {
                "id": "executive_blackout",
                "sort_key": "22:10:00",
                "time": "10:10 PM",
                "title": "Executive Floor Cameras Go Dark",
                "description": (
                    "The executive floor security cameras were offline during a critical "
                    "window, concealing activity on that floor."
                ),
                "location": "Security System",
                "event_type": "SYSTEM",
                "unlocked_by": {
                    "any": [
                        "access_during_blackout",
                        "blackout_during_struggle",
                        "security_override_access",
                        "sophie_systems_lie"
                    ]
                },
                "clarifications": [
                    {
                        "when": "blackout_during_struggle",
                        "time": "10:10 PM – 10:28 PM",
                        "title": "Blackout During the Struggle",
                        "description": (
                            "The estimated struggle at 10:24 PM happened while the executive "
                            "floor cameras were dark, giving the killer a concealed window."
                        )
                    },
                    {
                        "when": "sophie_systems_lie",
                        "time": "10:10 PM – 10:28 PM",
                        "title": "Blackout Missed During System Check",
                        "description": (
                            "Sophie said the systems looked normal, but the executive floor "
                            "cameras were manually blacked out from 10:10 PM to 10:28 PM."
                        ),
                        "event_type": "DEDUCTION"
                    },
                    {
                        "when": "security_override_access",
                        "time": "10:10 PM",
                        "title": "Security Console Login",
                        "description": (
                            "A security administrator account was used to manually override "
                            "the CCTV system at 10:10 PM. This was not a random failure."
                        ),
                        "event_type": "ACCESS"
                    }
                ]
            },
            {
                "id": "gap_blackout",
                "kind": "gap",
                "sort_key": "22:11:00",
                "time": "10:10 PM – 10:28 PM",
                "title": "Investigation Gap",
                "description": (
                    "The executive floor cameras were dark. Further evidence may clarify "
                    "what happened during this period."
                ),
                "unlocked_by": {
                    "any": [
                        "access_during_blackout",
                        "blackout_during_struggle",
                        "security_override_access",
                        "sophie_systems_lie"
                    ]
                },
                "hidden_when_any": ["elena_badge_access", "struggle"]
            },
            {
                "id": "elena_badge_access",
                "sort_key": "22:12:00",
                "time": "10:12 PM",
                "title": "Restricted Access Detected",
                "description": (
                    "An access card was used on the executive floor while the cameras "
                    "were offline."
                ),
                "location": "Executive Floor",
                "event_type": "ACCESS",
                "unlocked_by": {
                    "any": ["access_during_blackout", "elena_murder_window", "elena_access_lie"]
                },
                "clarifications": [
                    {
                        "when": "access_during_blackout",
                        "title": "Access During the Blackout",
                        "description": (
                            "Elena Vasquez's access card was used at 10:12 PM, while the "
                            "executive floor security cameras were offline."
                        )
                    },
                    {
                        "when": "elena_murder_window",
                        "title": "Badge Used Minutes Before the Struggle",
                        "description": (
                            "Elena's card was used on the executive floor at 10:12 PM, "
                            "only minutes before the victim's watch stopped at 10:24 PM."
                        )
                    },
                    {
                        "when": "elena_access_lie",
                        "title": "Elena's Card Used After She Claimed to Leave",
                        "description": (
                            "Elena claims she left before 10 PM and did not access the "
                            "executive floor, but her card was used there at 10:12 PM."
                        ),
                        "event_type": "DEDUCTION"
                    }
                ]
            },
            {
                "id": "coordinated_window",
                "sort_key": "22:11:30",
                "time": "10:10 PM – 10:12 PM",
                "title": "Coordinated Access Window",
                "description": (
                    "The security administrator login and Elena's badge use happened "
                    "within minutes of each other, suggesting a coordinated breach."
                ),
                "location": "Executive Floor",
                "event_type": "DEDUCTION",
                "unlocked_by": "coordinated_access_window"
            },
            {
                "id": "struggle",
                "sort_key": "22:24:00",
                "time": "10:24 PM",
                "title": "Struggle in the Victim's Office",
                "description": (
                    "The victim's broken watch stopped at 10:24 PM, marking the "
                    "approximate time of the struggle."
                ),
                "location": "Victim's Office",
                "event_type": "SCENE",
                "unlocked_by": {
                    "any": [
                        "blackout_during_struggle",
                        "elena_murder_window",
                        "marcus_unverified_window",
                        "financial_coverup_window",
                        "noah_confirmed_elsewhere"
                    ]
                }
            },
            {
                "id": "cameras_resume",
                "sort_key": "22:28:00",
                "time": "10:28 PM",
                "title": "CCTV Recording Resumes",
                "description": (
                    "The executive floor cameras resume recording after the manual "
                    "override window ends."
                ),
                "location": "Security System",
                "event_type": "SYSTEM",
                "unlocked_by": {
                    "any": [
                        "blackout_during_struggle",
                        "security_override_access",
                        "sophie_systems_lie"
                    ]
                }
            },
            {
                "id": "noah_leaves_server",
                "sort_key": "22:47:00",
                "time": "10:47 PM",
                "title": "Noah Leaves the Server Room",
                "description": (
                    "Server-room footage shows Noah remaining inside until 10:47 PM, "
                    "after the estimated struggle and after cameras on the executive floor resume."
                ),
                "location": "Server Room",
                "event_type": "SYSTEM",
                "unlocked_by": "noah_confirmed_elsewhere",
                "clarifications": [
                    {
                        "when": "noah_q2",
                        "title": "Noah's Account Matches the Camera Window",
                        "description": (
                            "Noah says he stayed in the server room until around 10:45 PM. "
                            "The isolated camera record shows him leaving at 10:47 PM."
                        ),
                        "event_type": "WITNESS"
                    }
                ]
            },
            {
                "id": "sophie_systems_and_scene",
                "sort_key": "22:10:30",
                "time": "Same night",
                "title": "Sophie Tied to Systems and Scene",
                "description": (
                    "Sophie's security-admin link and lipstick trace place her close to "
                    "both the blackout systems and the victim's office on the same night."
                ),
                "location": "Security Office / Victim's Office",
                "event_type": "DEDUCTION",
                "unlocked_by": "sophie_security_overlap"
            }
        ]

    def has_asked_question(self, question_id):
        return any(question_id in asked for asked in self.asked_questions.values())

    def is_timeline_requirement_met(self, requires):
        if requires is None:
            return True
        if isinstance(requires, dict):
            if "any" in requires:
                return any(self.is_timeline_requirement_met(item) for item in requires["any"])
            if "all" in requires:
                return all(self.is_timeline_requirement_met(item) for item in requires["all"])
            if "when" in requires:
                return self.is_timeline_requirement_met(requires["when"])
            return False
        if isinstance(requires, (list, tuple, set)):
            return all(self.is_timeline_requirement_met(item) for item in requires)
        if requires in self.discovered_leads:
            return True
        return self.has_asked_question(requires)

    def is_timeline_event_unlocked(self, event):
        if not self.is_timeline_requirement_met(event.get("unlocked_by")):
            return False
        hidden_when = event.get("hidden_when_any") or []
        if not hidden_when:
            return True
        visible_ids = {
            item["id"]
            for item in self.timeline_events
            if item.get("kind") != "gap"
            and item["id"] != event["id"]
            and self.is_timeline_requirement_met(item.get("unlocked_by"))
        }
        return not any(event_id in visible_ids for event_id in hidden_when)

    def resolve_timeline_event(self, event):
        resolved = dict(event)
        resolved["kind"] = event.get("kind", "event")
        for clarification in event.get("clarifications", []):
            if self.is_timeline_requirement_met(clarification.get("when")):
                for field in ("title", "description", "time", "event_type", "location"):
                    if field in clarification:
                        resolved[field] = clarification[field]
        return resolved

    def get_resolved_timeline_events(self):
        events = []
        for event in self.timeline_events:
            if event.get("kind") == "gap":
                continue
            if self.is_timeline_event_unlocked(event):
                events.append(self.resolve_timeline_event(event))
        events.sort(key=lambda item: (item["sort_key"], item["id"]))
        return events

    def get_timeline_display_items(self):
        items = []
        for event in self.timeline_events:
            if self.is_timeline_event_unlocked(event):
                items.append(self.resolve_timeline_event(event))
        items.sort(key=lambda item: (item["sort_key"], item.get("kind") == "event", item["id"]))
        return items

    def capture_timeline_state(self):
        return {
            item["id"]: (item["title"], item["description"])
            for item in self.get_resolved_timeline_events()
        }

    def diff_timeline_state(self, before_events):
        timeline_new = []
        timeline_updated = []
        for item in self.get_resolved_timeline_events():
            key = (item["title"], item["description"])
            if item["id"] not in before_events:
                timeline_new.append(item)
            elif before_events[item["id"]] != key:
                timeline_updated.append(item)
        return {"timeline_new": timeline_new, "timeline_updated": timeline_updated}

    def get_configured_timeline_event_count(self):
        return sum(1 for event in self.timeline_events if event.get("kind") != "gap")

    def get_discovered_timeline_event_count(self):
        return len(self.get_resolved_timeline_events())

    def get_timeline_progress(self):
        return self.get_discovered_timeline_event_count(), self.get_configured_timeline_event_count()

    def collect_asked_question_timeline_changes(self):
        return self.diff_timeline_state(self.capture_timeline_state())

    def open_timeline(self, widgets_to_close=None, focus_event_id=None):
        if widgets_to_close:
            for widget in widgets_to_close:
                if widget and widget.winfo_exists():
                    widget.destroy()
        self.pending_timeline_focus = focus_event_id
        self.show_page("timeline")

    def scroll_to_timeline_event(self, event_id):
        widget = self.timeline_event_widgets.get(event_id)
        canvas = self.main_frame._parent_canvas
        self.update_idletasks()
        if not widget or not widget.winfo_exists():
            canvas.yview_moveto(0)
            return
        inner_height = max(self.main_frame.winfo_height(), 1)
        canvas_height = max(canvas.winfo_height(), 1)
        if inner_height <= canvas_height:
            canvas.yview_moveto(0)
            return
        target = max(0.0, min(1.0, (widget.winfo_y() - 24) / inner_height))
        canvas.yview_moveto(target)

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
            text_color=self.theme["accent"]
        )
        breadcrumb.pack(anchor="w")

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 32, "bold"),
            text_color=self.theme["heading"]
        )
        title_label.pack(anchor="w", pady=(6, 4))

        subtitle_label = ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Arial", 14),
            text_color=self.theme["muted"]
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

    def get_timeline_focus_id(self, timeline_new=None, timeline_updated=None):
        if timeline_new:
            return timeline_new[0]["id"]
        if timeline_updated:
            return timeline_updated[0]["id"]
        return None

    def show_discovery_modal(
        self,
        finding_id,
        widgets_to_close=None,
        unlocked_questions=None,
        timeline_new=None,
        timeline_updated=None,
        headline_event=None,
        progression=None
    ):
        if progression:
            unlocked_questions = progression.get("questions", unlocked_questions)
            timeline_new = progression.get("timeline_new", timeline_new)
            timeline_updated = progression.get("timeline_updated", timeline_updated)

        unlocked_questions = unlocked_questions or []
        timeline_new = timeline_new or []
        timeline_updated = timeline_updated or []
        finding_data = self.findings_metadata.get(finding_id) if finding_id else None

        if not finding_data and not timeline_new and not timeline_updated:
            return

        modal = ctk.CTkFrame(
            self,
            width=540,
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")

        if finding_data:
            header_text = "NEW LEAD DISCOVERED"
            source_text = self.get_finding_label(finding_data["source_type"])
            title_text = finding_data["title"]
            description_text = finding_data["description"]
        else:
            header_text = "TIMELINE UPDATED"
            focus_event = headline_event or (timeline_new or timeline_updated)[0]
            source_text = focus_event.get("time", "")
            title_text = focus_event["title"]
            description_text = focus_event["description"]

        title = ctk.CTkLabel(
            modal,
            text=header_text,
            font=("Arial", 16, "bold"),
            text_color=self.theme["warning"]
        )
        title.pack(pady=(30, 12))

        source_label = ctk.CTkLabel(
            modal,
            text=source_text,
            font=("Arial", 11, "bold"),
            text_color=self.theme["accent"]
        )
        source_label.pack(pady=(0, 10))

        finding_title = ctk.CTkLabel(
            modal,
            text=title_text,
            font=("Arial", 18, "bold"),
            text_color=self.theme["heading"]
        )
        finding_title.pack(pady=(0, 10))

        description = ctk.CTkLabel(
            modal,
            text=description_text,
            font=("Arial", 14),
            text_color=self.theme["text"],
            wraplength=420,
            justify="center"
        )
        description.pack(padx=35, pady=(0, 16))

        extras = []
        if finding_data and (timeline_new or timeline_updated):
            extras.append("Timeline Updated")
        if unlocked_questions:
            unlocked_suspects = []
            for question_data in unlocked_questions:
                suspect_name = self.get_suspect_name(question_data["suspect_id"])
                if suspect_name not in unlocked_suspects:
                    unlocked_suspects.append(suspect_name)
            extras.append("Interview Question Available  •  " + ", ".join(unlocked_suspects))

        if extras:
            extras_frame = ctk.CTkFrame(modal, fg_color=self.theme["card"], corner_radius=10)
            extras_frame.pack(padx=35, pady=(0, 18), fill="x")
            extras_title = ctk.CTkLabel(
                extras_frame,
                text="NEW",
                font=("Arial", 11, "bold"),
                text_color=self.theme["accent"]
            )
            extras_title.pack(anchor="w", padx=14, pady=(10, 4))
            for extra in extras:
                extra_label = ctk.CTkLabel(
                    extras_frame,
                    text="•  " + extra,
                    font=("Arial", 12, "bold"),
                    text_color=self.theme["text"]
                )
                extra_label.pack(anchor="w", padx=14, pady=2)
            spacer = ctk.CTkLabel(extras_frame, text="", height=8)
            spacer.pack()

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(pady=(0, 28))

        focus_event_id = self.get_timeline_focus_id(timeline_new, timeline_updated)
        close_targets = [modal] + (widgets_to_close or [])

        if timeline_new or timeline_updated:
            view_timeline_button = ctk.CTkButton(
                actions,
                text="VIEW TIMELINE",
                width=150,
                height=40,
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                text_color=self.theme["heading"],
                command=lambda: self.open_timeline(close_targets, focus_event_id)
            )
            view_timeline_button.pack(side="left", padx=(0, 8))

        if finding_data:
            view_button = ctk.CTkButton(
                actions,
                text="VIEW CASE FINDINGS",
                width=180,
                height=40,
                fg_color=self.theme["primary"] if not (timeline_new or timeline_updated) else self.theme["card"],
                hover_color=self.theme["primary_hover"] if not (timeline_new or timeline_updated) else self.theme["border"],
                text_color=self.theme["heading"],
                command=lambda: self.open_case_findings(close_targets)
            )
            view_button.pack(side="left", padx=(0, 8))

        continue_button = ctk.CTkButton(
            actions,
            text="CONTINUE",
            width=120,
            height=40,
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"],
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
                fg_color=self.theme["card"],
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
                text_color=self.theme["heading"]
            )

            number_label.pack(
                pady=(18, 2)
            )

            text_label = ctk.CTkLabel(
                card,
                text=label,
                font=("Arial", 11, "bold"),
                text_color=self.theme["muted"]
            )

            text_label.pack(
                pady=(0, 18)
            )

        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
                text_color=self.theme["text"],
                justify="left",
                wraplength=800
            )

            lead_label.pack(
                anchor="w",
                padx=20,
                pady=5
            )

        timeline_discovered, timeline_total = self.get_timeline_progress()
        timeline_summary = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        timeline_summary.pack(fill="x", padx=40, pady=(0, 15))

        timeline_summary_title = ctk.CTkLabel(
            timeline_summary,
            text="TIMELINE RECONSTRUCTED",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        )
        timeline_summary_title.pack(anchor="w", padx=20, pady=(18, 8))

        timeline_summary_count = ctk.CTkLabel(
            timeline_summary,
            text=f"{timeline_discovered} / {timeline_total} EVENTS DISCOVERED",
            font=("Arial", 18, "bold"),
            text_color=self.theme["heading"]
        )
        timeline_summary_count.pack(anchor="w", padx=20, pady=(0, 8))

        timeline_summary_copy = ctk.CTkLabel(
            timeline_summary,
            text="The night is reconstructed as connections, contradictions, and interviews fill in missing time.",
            font=("Arial", 14),
            text_color=self.theme["text"],
            justify="left",
            wraplength=800
        )
        timeline_summary_copy.pack(anchor="w", padx=20, pady=(0, 18))

        next_lead_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["heading"],
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
                    text_color=self.theme["warning"]
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
                text_color=self.theme["muted"],
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
                fg_color=self.theme["card"],
                corner_radius=12,
                border_width=1,
                border_color=self.theme["border"]
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
                text_color=self.theme["heading"]
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
                text_color=self.theme["muted"]
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
                text_color=self.theme["accent"]
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
                text_color=self.theme["muted"]
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
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                text_color=self.theme["heading"],
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
            border_color=self.theme["border"],
            hover_color=self.theme["card"],
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"],
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
            text_color=self.theme["heading"]
        )

        evidence_title.pack(
            anchor="w",
            padx=40,
            pady=(5, 10)
        )

        for evidence in connected_evidence:

            evidence_card = ctk.CTkFrame(
                self.main_frame,
                fg_color=self.theme["card"],
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
                text_color=self.theme["heading"]
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
                text_color=self.theme["text"],
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
            text_color=self.theme["heading"]
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
            text_color=self.theme["muted"]
        )

        interview_subtitle.pack(
            anchor="w",
            padx=40,
            pady=(0, 12)
        )

        progress_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"]
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["accent"]
        )
        header_label.pack(
            pady=(25, 8)
        )

        suspect_label = ctk.CTkLabel(
            modal,
            text=suspect_name.upper(),
            font=("Arial", 24, "bold"),
            text_color=self.theme["heading"]
        )
        suspect_label.pack(
            pady=(0, 20)
        )

        # Divider
        divider = ctk.CTkFrame(
            modal,
            fg_color=self.theme["border"],
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["heading"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
            font=("Arial", 13, "bold"),
            corner_radius=8
        )
        ask_button.pack(
            pady=(0, 15)
        )

        # Response section
        response_frame = ctk.CTkFrame(
            modal,
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"],
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
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"],
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
            hover_color=self.theme["card"],
            text_color=self.theme["muted"],
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
            hover_color=self.theme["card"],
            text_color=self.theme["muted"],
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
            border_color=self.theme["border"],
            hover_color=self.theme["card"],
            text_color=self.theme["muted"],
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
                    question_label.configure(text=question, text_color=self.theme["heading"])
                    ask_button.configure(state="normal", fg_color=self.theme["card"], text_color=self.theme["heading"])

                    # Check if already asked
                    if question_data["id"] in asked_questions:
                        response_label.configure(text=answer, text_color=self.theme["text"])
                        if question_data.get("id") in self.contradictions:
                            present_evidence_button.pack(anchor="w", padx=20, pady=(10, 15))
                            present_evidence_button.configure(command=lambda q=question_data["id"]: self.show_evidence_selection(q, modal))
                        else:
                            present_evidence_button.pack_forget()
                    else:
                        response_label.configure(text="", text_color=self.theme["muted"])
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
                    question_label.configure(text="LOCKED — Further investigation required", text_color=self.theme["muted"])
                    ask_button.configure(state="disabled", fg_color=self.theme["background"], text_color=self.theme["muted"])
                    response_label.configure(text="", text_color=self.theme["muted"])
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
            label.configure(text="", text_color=self.theme["text"])
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
            callback = current_typing.pop("on_complete", None)
            if callback:
                callback()

    def ask_question(self, suspect_id, question_index, total_questions, question_data, response_label, counter_label, current_typing, btn=None, modal=None):
        before_events = self.capture_timeline_state()
        self.asked_questions.setdefault(suspect_id, set()).add(question_data["id"])
        self.update_case_progress()
        counter_label.configure(text=f"QUESTION {question_index + 1} OF {total_questions}  •  ASKED")
        timeline_changes = self.diff_timeline_state(before_events)

        if current_typing.get("id"):
            self.after_cancel(current_typing["id"])
            current_typing["id"] = None

        def after_answer():
            if not (timeline_changes["timeline_new"] or timeline_changes["timeline_updated"]):
                return
            widgets_to_close = [modal] if modal and modal.winfo_exists() else None
            self.show_discovery_modal(
                finding_id=None,
                widgets_to_close=widgets_to_close,
                timeline_new=timeline_changes["timeline_new"],
                timeline_updated=timeline_changes["timeline_updated"]
            )

        current_typing["on_complete"] = after_answer
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
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        
        modal_title = ctk.CTkLabel(
            modal,
            text="PRESENT EVIDENCE",
            font=("Arial", 18, "bold"),
            text_color=self.theme["heading"]
        )
        modal_title.pack(pady=(25, 15))

        instruction = ctk.CTkLabel(
            modal,
            text="Select evidence that challenges this statement:",
            font=("Arial", 13),
            text_color=self.theme["muted"]
        )
        instruction.pack(pady=(0, 15))
        
        selection_frame = ctk.CTkScrollableFrame(
            modal,
            fg_color=self.theme["card"],
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
                hover_color=self.theme["card"],
                text_color=self.theme["text"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            self.show_discovery_modal(deduction_id, widgets_to_close, progression=unlocked_questions)
            
        else:
            result_modal = ctk.CTkFrame(
                self, width=450, height=200, fg_color=self.theme["card"],
                corner_radius=15, border_width=1, border_color=self.theme["border"]
            )
            result_modal.place(relx=0.5, rely=0.5, anchor="center")
            
            title = ctk.CTkLabel(result_modal, text="NO CONTRADICTION FOUND", font=("Arial", 16, "bold"), text_color=self.theme["accent"])
            title.pack(pady=(30, 15))
            
            desc = ctk.CTkLabel(result_modal, text="This evidence does not directly challenge the suspect's statement.", font=("Arial", 14), text_color=self.theme["muted"])
            desc.pack(pady=(0, 25))
            
            close_btn = ctk.CTkButton(result_modal, text="CONTINUE INTERVIEW", width=180, height=35, fg_color=self.theme["card"], hover_color=self.theme["border"], text_color=self.theme["heading"], command=result_modal.destroy)
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
                fg_color=self.theme["card"],
                corner_radius=12,
                border_width=1,
                border_color=self.theme["border"],
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
                text_color=self.theme["heading"]
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
                text_color=self.theme["muted"]
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
                text_color=self.theme["text"],
                justify="left",
                wraplength=800
            )

            description_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 10)
            )

            importance_colors = {
                "Low": self.theme["importance_low"],
                "Medium": self.theme["importance_medium"],
                "High": self.theme["importance_high"],
                "Critical": self.theme["importance_critical"]
            }

            importance_label = ctk.CTkLabel(
                card,
                text=evidence["importance"].upper(),
                font=("Arial", 11, "bold"),
                text_color=importance_colors.get(
                    evidence["importance"],
                    self.theme["accent"]
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
                text_color=self.theme["accent"]
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
            hover_color=self.theme["card"],
            text_color=self.theme["accent"],
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"]
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
            text_color=self.theme["text"],
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
            text_color=self.theme["text"],
            anchor="w"
        )
        location_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        # Importance
        importance_colors = {
            "Low": self.theme["importance_low"],
            "Medium": self.theme["importance_medium"],
            "High": self.theme["importance_high"],
            "Critical": self.theme["importance_critical"]
        }
        importance_label = ctk.CTkLabel(
            info_frame,
            text=f"Importance: {evidence['importance'].upper()}",
            font=("Arial", 14, "bold"),
            text_color=importance_colors.get(
                evidence['importance'],
                self.theme["accent"]
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["accent"],
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
            text_color=self.theme["text"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["heading"]
        )
        modal_title.pack(
            pady=(25, 15)
        )

        # Instruction text
        instruction = ctk.CTkLabel(
            modal,
            text="Select another piece of evidence to connect with:",
            font=("Arial", 13),
            text_color=self.theme["muted"]
        )
        instruction.pack(
            pady=(0, 15)
        )

        # Evidence selection frame
        selection_frame = ctk.CTkFrame(
            modal,
            fg_color=self.theme["card"],
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
                hover_color=self.theme["card"],
                text_color=self.theme["text"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["accent"]
        )
        header_label.pack(
            pady=(25, 8)
        )

        # Clear question
        question_label = ctk.CTkLabel(
            modal,
            text="How are these clues connected?",
            font=("Arial", 15),
            text_color=self.theme["heading"]
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
            fg_color=self.theme["card"],
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
            text_color=self.theme["heading"],
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
            text_color=self.theme["accent"],
            width=30
        )
        connection_symbol.pack(
            side="left",
            padx=5
        )

        # Second evidence card
        evidence2_card = ctk.CTkFrame(
            evidence_container,
            fg_color=self.theme["card"],
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
            text_color=self.theme["heading"],
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
            text_color=self.theme["muted"]
        )
        connection_section_label.pack(
            pady=(0, 12)
        )

        # Selected connection display
        selected_label = ctk.CTkLabel(
            modal,
            text="",
            font=("Arial", 12),
            text_color=self.theme["accent"]
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
                hover_color=self.theme["card"],
                text_color=self.theme["text"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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
            hover_color=self.theme["card"],
            text_color=self.theme["muted"],
            corner_radius=8,
            command=modal.destroy
        )
        cancel_button.pack(
            pady=(0, 20)
        )

    def select_connection_type(self, connection_type, selected_dict, selected_label, buttons):
        selected_dict["value"] = connection_type
        selected_label.configure(text=f"Selected: {connection_type}", text_color=self.theme["accent"])
        
        # Reset all buttons to transparent
        for btn in buttons.values():
            btn.configure(fg_color="transparent", text_color=self.theme["text"])
        
        # Highlight selected button with blue accent
        buttons[connection_type].configure(fg_color=self.theme["primary"], text_color=self.theme["accent"])

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
                    self.show_discovery_modal(connection_data["id"], progression=unlocked_questions)
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
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["muted"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
            command=modal.destroy
        )
        close_button.pack()

    def show_connection_discovered_modal(self, connection_data):
        modal = ctk.CTkFrame(
            self,
            width=450,
            height=250,
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["warning"]
        )
        title.pack(
            pady=(30, 15)
        )

        # Lead title
        lead_title = ctk.CTkLabel(
            modal,
            text=connection_data["title"],
            font=("Arial", 16, "bold"),
            text_color=self.theme["heading"]
        )
        lead_title.pack(
            pady=(0, 10)
        )

        # Description
        description = ctk.CTkLabel(
            modal,
            text=connection_data["description"],
            font=("Arial", 13),
            text_color=self.theme["text"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
            command=modal.destroy
        )
        continue_button.pack()

    def show_invalid_connection_modal(self):
        modal = ctk.CTkFrame(
            self,
            width=400,
            height=180,
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["muted"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
            command=modal.destroy
        )
        close_button.pack()

    def show_already_discovered_modal(self, connection_title):
        modal = ctk.CTkFrame(
            self,
            width=400,
            height=180,
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
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
            text_color=self.theme["muted"],
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
            fg_color=self.theme["card"],
            hover_color=self.theme["border"],
            text_color=self.theme["heading"],
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

            # Empty state container
            empty_state_frame = ctk.CTkFrame(
                self.main_frame,
                fg_color=self.theme["card"],
                corner_radius=14,
                border_width=1,
                border_color=self.theme["border"]
            )

            empty_state_frame.pack(
                fill="x",
                padx=40,
                pady=(8, 20)
            )

            # Investigation icon
            empty_icon = ctk.CTkLabel(
                empty_state_frame,
                text="◌",
                font=("Arial", 34),
                text_color=self.theme["accent"]
            )

            empty_icon.pack(
                pady=(32, 8)
            )

            # Status label
            status_label = ctk.CTkLabel(
                empty_state_frame,
                text="INVESTIGATION IN PROGRESS",
                font=("Arial", 11, "bold"),
                text_color=self.theme["accent"]
            )

            status_label.pack(
                pady=(0, 8)
            )

            # Main title
            empty_title = ctk.CTkLabel(
                empty_state_frame,
                text="No findings documented yet",
                font=("Arial", 20, "bold"),
                text_color=self.theme["heading"]
            )

            empty_title.pack(
                pady=(0, 10)
            )

            # Description
            empty_description = ctk.CTkLabel(
                empty_state_frame,
                text=(
                    "Your case findings will appear here as you connect evidence, "
                    "expose contradictions, and uncover new leads."
                ),
                font=("Arial", 14),
                text_color=self.theme["muted"],
                wraplength=720,
                justify="center"
            )

            empty_description.pack(
                padx=50,
                pady=(0, 12)
            )

            # Next step hint
            next_step = ctk.CTkLabel(
                empty_state_frame,
                text="NEXT STEP  •  Review evidence and investigate possible connections",
                font=("Arial", 11, "bold"),
                text_color=self.theme["accent"]
            )

            next_step.pack(
                pady=(0, 32)
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
                    fg_color=self.theme["card"],
                    corner_radius=12,
                    border_width=1,
                    border_color=self.theme["border"]
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
                    text_color=self.theme["accent"]
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
                    text_color=self.theme["heading"]
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
                    text_color=self.theme["text"],
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
                        text_color=self.theme["muted"],
                        justify="left",
                        wraplength=800
                    )

                    evidence_label.pack(
                        anchor="w",
                        padx=20,
                        pady=(0, 18)
                    )

    def create_timeline_page(self):

        discovered, total = self.get_timeline_progress()

        self.create_page_header(
            "Timeline",
            f"Reconstruct the night as discoveries land. "
            f"{discovered} of {total} events documented.",
            "Timeline"
        )

        self.timeline_event_widgets = {}

        items = self.get_timeline_display_items()

        focus_id = self.pending_timeline_focus
        self.pending_timeline_focus = None

        rail = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        rail.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(0, 30)
        )

        for index, event in enumerate(items):

            is_gap = event.get("kind") == "gap"
            is_focus = event["id"] == focus_id

            timeline_row = ctk.CTkFrame(
                rail,
                fg_color="transparent"
            )

            timeline_row.pack(
                fill="x",
                pady=0
            )

            # Timeline Marker Column

            marker_column = ctk.CTkFrame(
                timeline_row,
                width=28,
                fg_color="transparent"
            )

            marker_column.pack(
                side="left",
                fill="y",
                padx=(0, 14)
            )

            marker_column.pack_propagate(False)

            if index > 0:

                top_line = ctk.CTkFrame(
                    marker_column,
                    width=2,
                    height=14,
                    fg_color=self.theme["border"],
                    corner_radius=1
                )

                top_line.pack(
                    pady=(0, 0)
                )

            # Timeline dot

            if is_focus:

                dot_color = self.theme["warning"]

            elif is_gap:

                dot_color = self.theme["muted"]

            else:

                dot_color = self.theme["accent"]

            dot = ctk.CTkLabel(
                marker_column,
                text="○" if is_gap else "●",
                font=("Arial", 16),
                text_color=dot_color,
                width=28
            )

            dot.pack()

            if index < len(items) - 1:

                bottom_line = ctk.CTkFrame(
                    marker_column,
                    width=2,
                    fg_color=self.theme["border"],
                    corner_radius=1
                )

                bottom_line.pack(
                    fill="y",
                    expand=True,
                    pady=(2, 0)
                )

            # Event Card

            if is_focus:

                border_color = self.theme["warning"]

            else:

                border_color = self.theme["border"]

            event_frame = ctk.CTkFrame(
                timeline_row,
                fg_color=self.theme["background"]
                if is_gap
                else self.theme["card"],
                corner_radius=12,
                border_width=1,
                border_color=border_color
            )

            event_frame.pack(
                side="left",
                fill="x",
                expand=True,
                pady=(0, 12)
            )

            self.timeline_event_widgets[
                event["id"]
            ] = event_frame

            # Time

            time_label = ctk.CTkLabel(
                event_frame,
                text=event["time"],
                font=("Arial", 16, "bold"),
                text_color=(
                    self.theme["muted"]
                    if is_gap
                    else self.theme["accent"]
                ),
                width=150,
                anchor="w"
            )

            time_label.pack(
                side="left",
                padx=(20, 12),
                pady=20
            )

            # Event Details

            details_frame = ctk.CTkFrame(
                event_frame,
                fg_color="transparent"
            )

            details_frame.pack(
                side="left",
                fill="both",
                expand=True,
                pady=16,
                padx=(0, 20)
            )

            header_row = ctk.CTkFrame(
                details_frame,
                fg_color="transparent"
            )

            header_row.pack(
                fill="x"
            )

            event_label = ctk.CTkLabel(
                header_row,
                text=event["title"],
                font=("Arial", 16, "bold"),
                text_color=(
                    self.theme["muted"]
                    if is_gap
                    else self.theme["heading"]
                ),
                justify="left",
                wraplength=560,
                anchor="w"
            )

            event_label.pack(
                side="left",
                anchor="w"
            )

            # Event type badge

            if not is_gap:

                type_label = ctk.CTkLabel(
                    header_row,
                    text=event.get(
                        "event_type",
                        "EVENT"
                    ),
                    font=("Arial", 11, "bold"),
                    text_color=self.theme["accent"],
                    fg_color=self.theme["background"],
                    corner_radius=8,
                    padx=8,
                    pady=2
                )

                type_label.pack(
                    side="right",
                    padx=(12, 0)
                )

            # Description

            description_label = ctk.CTkLabel(
                details_frame,
                text=event["description"],
                font=("Arial", 13),
                text_color=(
                    self.theme["muted"]
                    if is_gap
                    else self.theme["text"]
                ),
                justify="left",
                wraplength=650,
                anchor="w"
            )

            description_label.pack(
                anchor="w",
                pady=(6, 0)
            )

            # Location

            if event.get("location") and not is_gap:

                location_label = ctk.CTkLabel(
                    details_frame,
                    text=event["location"],
                    font=("Arial", 12),
                    text_color=self.theme["muted"]
                )

                location_label.pack(
                    anchor="w",
                    pady=(6, 0)
                )

        if focus_id:

            self.after(
                80,
                lambda:
                    self.scroll_to_timeline_event(
                        focus_id
                    )
            )

    def show_settings_page(self):

        # Reset scroll position
        self.main_frame._parent_canvas.yview_moveto(0)

        # Page Header

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(40, 10)
        )

        title = ctk.CTkLabel(
            header,
            text="SETTINGS",
            font=("Arial", 32, "bold"),
            text_color=self.theme["heading"]
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Customize your CASEFILE investigation workspace.",
            font=("Arial", 14),
            text_color=self.theme["muted"]
        )

        subtitle.pack(
            anchor="w",
            pady=(5, 0)
        )

        # Appearance Card

        appearance_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        appearance_card.pack(
            fill="x",
            padx=40,
            pady=(25, 20)
        )

        appearance_title = ctk.CTkLabel(
            appearance_card,
            text="APPEARANCE",
            font=("Arial", 14, "bold"),
            text_color=self.theme["accent"]
        )

        appearance_title.pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        appearance_subtitle = ctk.CTkLabel(
            appearance_card,
            text="Choose the visual style of your investigation interface.",
            font=("Arial", 13),
            text_color=self.theme["muted"]
        )

        appearance_subtitle.pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        descriptions = {
            "Midnight Blue":
                "The original CASEFILE investigation interface.",

            "Crimson Noir":
                "A darker, tense atmosphere with deep crimson accents.",

            "Emerald Investigation":
                "A calm investigative environment with emerald tones.",

            "Monochrome":
                "A minimal grayscale interface with a noir aesthetic."
        }

        # Theme Cards

        for theme_name, colors in THEMES.items():

            is_selected = (
                theme_name == self.current_theme
            )

            card_color = (
                self.theme["background"]
            )

            theme_card = ctk.CTkFrame(
                appearance_card,
                fg_color=card_color,
                corner_radius=10,
                border_width=2 if is_selected else 1,
                border_color=(
                    colors["primary"]
                    if is_selected
                    else self.theme["border"]
                )
            )

            theme_card.pack(
                fill="x",
                padx=25,
                pady=7
            )

            # Left side information
            info_frame = ctk.CTkFrame(
                theme_card,
                fg_color="transparent"
            )

            info_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(18, 10),
                pady=15
            )

            theme_title = ctk.CTkLabel(
                info_frame,
                text=theme_name,
                font=("Arial", 15, "bold"),
                text_color=self.theme["heading"]
            )

            theme_title.pack(
                anchor="w"
            )

            description = ctk.CTkLabel(
                info_frame,
                text=descriptions[theme_name],
                font=("Arial", 12),
                text_color=self.theme["muted"]
            )

            description.pack(
                anchor="w",
                pady=(4, 0)
            )

            # Color preview
            preview_frame = ctk.CTkFrame(
                theme_card,
                fg_color="transparent"
            )

            preview_frame.pack(
                side="right",
                padx=(10, 18)
            )

            for color_key in [
                "background",
                "sidebar",
                "card",
                "primary",
                "accent"
            ]:

                preview = ctk.CTkFrame(
                    preview_frame,
                    width=18,
                    height=18,
                    corner_radius=9,
                    fg_color=colors[color_key]
                )

                preview.pack(
                    side="left",
                    padx=3
                )

            # Active indicator
            if is_selected:

                active_label = ctk.CTkLabel(
                    theme_card,
                    text="✓ ACTIVE",
                    font=("Arial", 11, "bold"),
                    text_color=colors["accent"]
                )

                active_label.pack(
                    side="right",
                    padx=(0, 15)
                )

            # Select theme
            select_button = ctk.CTkButton(
                theme_card,
                text="SELECTED" if is_selected else "SELECT",
                width=100,
                height=34,
                font=("Arial", 11, "bold"),
                fg_color=(
                    colors["primary"]
                    if is_selected
                    else self.theme["primary"]
                ),
                hover_color=colors["primary_hover"],
                text_color=self.theme["heading"],
                state="disabled" if is_selected else "normal",
                command=lambda name=theme_name: self.set_theme(name)
            )

            select_button.pack(
                side="right",
                padx=(0, 10)
            )

        # Bottom spacing
        ctk.CTkFrame(
            self.main_frame,
            height=30,
            fg_color="transparent"
        ).pack()

    def load_settings(self):

        settings_path = os.path.expanduser(
            "~/.casefile_settings.json"
        )

        try:

            if os.path.exists(settings_path):

                with open(settings_path, "r") as file:

                    settings = json.load(file)

                    saved_theme = settings.get(
                        "theme",
                        "Midnight Blue"
                    )

                    if saved_theme in THEMES:

                        return saved_theme

        except (
            json.JSONDecodeError,
            OSError
        ):

            pass

        return "Midnight Blue"

    def apply_theme(self):

        # Root window
        self.configure(
            fg_color=self.theme["background"]
        )

        # Sidebar
        if hasattr(self, "sidebar"):
            self.sidebar.configure(
                fg_color=self.theme["sidebar"]
            )

        # Main content area
        if hasattr(self, "main_frame"):
            self.main_frame.configure(
                fg_color=self.theme["background"]
            )

        # Sidebar navigation buttons
        if hasattr(self, "nav_buttons"):
            for button in self.nav_buttons.values():
                button.configure(
                    text_color=self.theme["text"],
                    hover_color=self.theme["primary_hover"]
                )

        # Navigation badges
        if hasattr(self, "nav_badges"):
            for badge in self.nav_badges.values():
                badge.configure(
                    fg_color=self.theme["card"],
                    text_color=self.theme["accent"]
                )

        if hasattr(self, "case_label"):
            self.case_label.configure(
                text_color=self.theme["accent"]
            )

    def set_theme(self, theme_name):

        if theme_name not in THEMES:
            return

        self.current_theme = theme_name
        self.theme = THEMES[theme_name]

        self.save_settings()
        self.apply_theme()

        # Refresh the current page with the new theme
        current_page = self.current_page
        self.show_page(current_page)

    def save_settings(self):

        settings_path = os.path.expanduser(
            "~/.casefile_settings.json"
        )

        try:

            with open(settings_path, "w") as file:

                json.dump(
                    {
                        "theme": self.current_theme
                    },
                    file
                )

        except OSError:

            pass

    def check_resolution_unlock(self):
        """Check if case resolution should be unlocked based on discoveries"""
        if self.resolution_unlocked or self.case_closed:
            return

        config = self.resolution_config["unlock_conditions"]
        
        # Check if required findings are discovered
        required_findings = config["required_findings"]
        findings_met = all(finding in self.discovered_leads for finding in required_findings)
        
        # Check if required contradictions are exposed
        required_contradictions = config["required_contradictions"]
        contradictions_met = all(contradiction in self.discovered_leads for contradiction in required_contradictions)
        
        if findings_met and contradictions_met:
            self.resolution_unlocked = True
            self.show_resolution_unlock_modal()

    def show_resolution_unlock_modal(self):
        """Show modal when case resolution becomes available"""
        modal = ctk.CTkFrame(
            self,
            width=500,
            height=280,
            fg_color=self.theme["card"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Header
        header = ctk.CTkLabel(
            modal,
            text="NEW OBJECTIVE UNLOCKED",
            font=("Arial", 18, "bold"),
            text_color=self.theme["warning"]
        )
        header.pack(
            pady=(30, 15)
        )

        # Message
        message = ctk.CTkLabel(
            modal,
            text="CASE RESOLUTION AVAILABLE",
            font=("Arial", 16, "bold"),
            text_color=self.theme["heading"]
        )
        message.pack(
            pady=(0, 10)
        )

        description = ctk.CTkLabel(
            modal,
            text="The evidence now allows you to attempt a reconstruction of the events.",
            font=("Arial", 13),
            text_color=self.theme["muted"],
            wraplength=450,
            justify="center"
        )
        description.pack(
            padx=30,
            pady=(0, 25)
        )

        # Button
        continue_button = ctk.CTkButton(
            modal,
            text="CONTINUE INVESTIGATION",
            width=200,
            height=40,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"],
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=modal.destroy
        )
        continue_button.pack()

    def show_case_resolution_page(self):
        """Show the case resolution page"""
        # Header
        title = ctk.CTkLabel(
            self.main_frame,
            text="CASE RESOLUTION",
            font=("Arial", 32, "bold"),
            text_color=self.theme["heading"]
        )
        title.pack(
            anchor="w",
            padx=40,
            pady=(40, 5)
        )

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Construct your final theory based on the evidence you have discovered.",
            font=("Arial", 14),
            text_color=self.theme["muted"]
        )
        subtitle.pack(
            anchor="w",
            padx=40,
            pady=(0, 25)
        )

        if self.case_closed:
            self.show_case_closed_state()
        elif not self.resolution_unlocked:
            self.show_resolution_locked()
        else:
            self.show_resolution_interface()

    def show_resolution_locked(self):
        """Show locked state when resolution not yet available"""
        locked_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        locked_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        locked_icon = ctk.CTkLabel(
            locked_frame,
            text="🔒",
            font=("Arial", 32),
            text_color=self.theme["muted"]
        )
        locked_icon.pack(
            pady=(40, 15)
        )

        locked_title = ctk.CTkLabel(
            locked_frame,
            text="CASE RESOLUTION LOCKED",
            font=("Arial", 18, "bold"),
            text_color=self.theme["heading"]
        )
        locked_title.pack(
            pady=(0, 10)
        )

        locked_message = ctk.CTkLabel(
            locked_frame,
            text="More investigation is required before you can attempt to resolve this case.",
            font=("Arial", 14),
            text_color=self.theme["muted"],
            wraplength=800,
            justify="center"
        )
        locked_message.pack(
            padx=40,
            pady=(0, 15)
        )

        requirements_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        requirements_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        req_title = ctk.CTkLabel(
            requirements_frame,
            text="REQUIREMENTS",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        )
        req_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        config = self.resolution_config["unlock_conditions"]
        
        # Show required findings progress
        findings_req = ctk.CTkLabel(
            requirements_frame,
            text=f"Critical Findings: {sum(1 for f in config['required_findings'] if f in self.discovered_leads)} / {len(config['required_findings'])}",
            font=("Arial", 13),
            text_color=self.theme["text"],
            anchor="w"
        )
        findings_req.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        # Show contradictions progress
        contr_req = ctk.CTkLabel(
            requirements_frame,
            text=f"Contradictions Exposed: {sum(1 for c in config['required_contradictions'] if c in self.discovered_leads)} / {len(config['required_contradictions'])}",
            font=("Arial", 13),
            text_color=self.theme["text"],
            anchor="w"
        )
        contr_req.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    def show_resolution_interface(self):
        """Show the interactive case resolution interface."""

        self.current_theory = {
            "suspect_id": None,
            "timeline_choice": None,
            "method_choice": None,
            "motive_choice": None,
            "evidence_ids": set()
        }

        # GET SUSPECTS

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM suspects
            ORDER BY id
        """)

        suspects = cursor.fetchall()

        cursor.close()
        connection.close()

        # MAIN GRID

        theory_grid = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        theory_grid.pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        theory_grid.grid_columnconfigure(0, weight=1)
        theory_grid.grid_columnconfigure(1, weight=1)

        # 01 — WHO

        who_frame = ctk.CTkFrame(
            theory_grid,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        who_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
            pady=(0, 8)
        )

        ctk.CTkLabel(
            who_frame,
            text="01  WHO DID IT?",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            who_frame,
            text="Select who you believe is responsible.",
            font=("Arial", 11),
            text_color=self.theme["muted"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )


        suspect_grid = ctk.CTkFrame(
            who_frame,
            fg_color="transparent"
        )

        suspect_grid.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        suspect_grid.grid_columnconfigure(0, weight=1)
        suspect_grid.grid_columnconfigure(1, weight=1)

        self.suspect_selection_buttons = {}

        for index, suspect in enumerate(suspects):

            row = index // 2
            column = index % 2

            button = ctk.CTkButton(
                suspect_grid,
                text=suspect["name"],
                font=("Arial", 12, "bold"),
                height=42,
                fg_color="transparent",
                hover_color=self.theme["primary_hover"],
                border_width=1,
                border_color=self.theme["border"],
                text_color=self.theme["text"],
                command=lambda suspect_id=suspect["id"]:
                    self.select_resolution_suspect(suspect_id)
            )

            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=4,
                pady=4
            )

            self.suspect_selection_buttons[
                suspect["id"]
            ] = button

        # 02 — WHEN

        timeline_frame = ctk.CTkFrame(
            theory_grid,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        timeline_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
            pady=(0, 8)
        )

        ctk.CTkLabel(
            timeline_frame,
            text="02  WHEN?",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            timeline_frame,
            text="Identify when the critical events occurred.",
            font=("Arial", 11),
            text_color=self.theme["muted"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.timeline_selection_var = ctk.StringVar(
            value=""
        )

        timeline_options = [
            "During the 10:10–10:28 PM security blackout",
            "After the cameras resumed recording",
            "Before the security blackout"
        ]

        for option in timeline_options:

            radio = ctk.CTkRadioButton(
                timeline_frame,
                text=option,
                variable=self.timeline_selection_var,
                value=option,
                font=("Arial", 12),
                text_color=self.theme["text"],
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                border_color=self.theme["border"]
            )

            radio.pack(
                anchor="w",
                padx=20,
                pady=6
            )

        ctk.CTkFrame(
            timeline_frame,
            height=10,
            fg_color="transparent"
        ).pack()

        # 03 — HOW

        method_frame = ctk.CTkFrame(
            theory_grid,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        method_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 8),
            pady=(8, 0)
        )

        ctk.CTkLabel(
            method_frame,
            text="03  HOW?",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            method_frame,
            text="Choose the method supported by the evidence.",
            font=("Arial", 11),
            text_color=self.theme["muted"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.method_selection_var = ctk.StringVar(
            value=""
        )

        method_options = [
            "Used security administrator access to disable cameras",
            "Forced entry during the blackout period",
            "Used stolen access credentials",
            "Exploited a system vulnerability"
        ]

        for option in method_options:

            radio = ctk.CTkRadioButton(
                method_frame,
                text=option,
                variable=self.method_selection_var,
                value=option,
                font=("Arial", 12),
                text_color=self.theme["text"],
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                border_color=self.theme["border"]
            )

            radio.pack(
                anchor="w",
                padx=20,
                pady=6
            )

        ctk.CTkFrame(
            method_frame,
            height=10,
            fg_color="transparent"
        ).pack()

        # 04 — WHY

        motive_frame = ctk.CTkFrame(
            theory_grid,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        motive_frame.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(8, 0),
            pady=(8, 0)
        )

        ctk.CTkLabel(
            motive_frame,
            text="04  WHY?",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            motive_frame,
            text="Choose the motive behind the crime.",
            font=("Arial", 11),
            text_color=self.theme["muted"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.motive_selection_var = ctk.StringVar(
            value=""
        )

        motive_options = [
            "Financial pressure from discovered records",
            "Threat of being removed from the company",
            "Evidence tampering to conceal access",
            "Personal conflict with the victim"
        ]

        for option in motive_options:

            radio = ctk.CTkRadioButton(
                motive_frame,
                text=option,
                variable=self.motive_selection_var,
                value=option,
                font=("Arial", 12),
                text_color=self.theme["text"],
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                border_color=self.theme["border"]
            )

            radio.pack(
                anchor="w",
                padx=20,
                pady=6
            )

        ctk.CTkFrame(
            motive_frame,
            height=10,
            fg_color="transparent"
        ).pack()

        # 05 — SUPPORTING EVIDENCE

        evidence_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=14,
            border_width=1,
            border_color=self.theme["border"]
        )

        evidence_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 18)
        )

        ctk.CTkLabel(
            evidence_frame,
            text="05  SUPPORTING EVIDENCE",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            evidence_frame,
            text="Select the evidence that supports your final theory.",
            font=("Arial", 11),
            text_color=self.theme["muted"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        # Load all evidence

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM evidence
            ORDER BY id
        """)

        available_evidence = cursor.fetchall()

        cursor.close()
        connection.close()


        evidence_grid = ctk.CTkFrame(
            evidence_frame,
            fg_color="transparent"
        )

        evidence_grid.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        evidence_grid.grid_columnconfigure(0, weight=1)
        evidence_grid.grid_columnconfigure(1, weight=1)

        self.evidence_checkboxes = {}

        for index, evidence in enumerate(available_evidence):

            row = index // 2
            column = index % 2

            checkbox = ctk.CTkCheckBox(
                evidence_grid,
                text=evidence["title"],
                font=("Arial", 12),
                text_color=self.theme["text"],
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                border_color=self.theme["border"],
                checkbox_width=20,
                checkbox_height=20
            )

            checkbox.grid(
                row=row,
                column=column,
                sticky="w",
                padx=8,
                pady=7
            )

            self.evidence_checkboxes[
                evidence["id"]
            ] = checkbox

        # Submit

        submit_button = ctk.CTkButton(
            self.main_frame,
            text="SUBMIT CASE THEORY  →",
            width=280,
            height=52,
            corner_radius=10,
            font=("Arial", 15, "bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"],
            command=self.analyze_case_theory
        )

        submit_button.pack(
            pady=(5, 35)
        )

    def select_resolution_suspect(self, suspect_id):
        """Handle suspect selection in resolution interface"""
        self.current_theory["suspect_id"] = suspect_id
        
        # Update button states
        for sid, btn in self.suspect_selection_buttons.items():
            if sid == suspect_id:
                btn.configure(
                    fg_color=self.theme["primary"],
                    text_color=self.theme["heading"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.theme["text"]
                )

    def analyze_case_theory(self):
        """Analyze the submitted case theory"""

        theory = self.current_theory.copy()

        # Collect radio-button selections
        theory["timeline_choice"] = self.timeline_selection_var.get()
        theory["method_choice"] = self.method_selection_var.get()
        theory["motive_choice"] = self.motive_selection_var.get()

        # Collect evidence selections
        selected_evidence = set()

        for evidence_id, checkbox in self.evidence_checkboxes.items():
            if checkbox.get():
                selected_evidence.add(evidence_id)

        theory["evidence_ids"] = selected_evidence

        # Keep the current theory in sync
        self.current_theory = theory

        results = {
            "suspect": self.analyze_suspect_choice(theory),
            "timeline": self.analyze_timeline_choice(theory),
            "method": self.analyze_method_choice(theory),
            "motive": self.analyze_motive_choice(theory),
            "evidence": self.analyze_evidence_support(theory)
        }

        self.show_theory_analysis(results)

    def analyze_suspect_choice(self, theory):
        """Analyze if the suspect choice is supported by evidence"""
        if theory["suspect_id"] is None:
            return {"valid": False, "message": "No suspect was selected."}
        
        correct_solution = self.resolution_config["correct_solution"]
        
        if theory["suspect_id"] == correct_solution["suspect_id"]:
            # Check if supporting evidence exists
            required_evidence = set(correct_solution["supporting_evidence_ids"])
            has_evidence = len(theory["evidence_ids"] & required_evidence) >= correct_solution["required_evidence_count"]
            
            if has_evidence:
                return {"valid": True, "message": "Suspect identification is supported by evidence."}
            else:
                return {"valid": False, "message": "Insufficient evidence links this suspect to the crime scene."}
        else:
            return {"valid": False, "message": "The selected suspect's involvement is not established by your current evidence."}

    def analyze_timeline_choice(self, theory):

        """Analyze the selected timeline."""

        timeline_choice = theory["timeline_choice"]

        if not timeline_choice:
            return {
                "valid": False,
                "message": "No timeline reconstruction was provided."
            }

        correct_timeline = (
            "During the 10:10–10:28 PM security blackout"
        )

        if timeline_choice == correct_timeline:
            return {
                "valid": True,
                "message": "Timeline is consistent with the established events."
            }

        return {
            "valid": False,
            "message": "Your timeline is inconsistent with the established sequence of events."
        }

    def analyze_method_choice(self, theory):

        """Analyze the selected method."""

        method_choice = theory["method_choice"]

        if not method_choice:
            return {
                "valid": False,
                "message": "No method was specified."
            }

        correct_method = (
            "Used security administrator access to disable cameras"
        )

        if method_choice == correct_method:
            return {
                "valid": True,
                "message": "Method is supported by the security system evidence."
            }

        return {
            "valid": False,
            "message": "The selected method is not sufficiently supported by the evidence."
        }

    def analyze_motive_choice(self, theory):

        motive_choice = theory["motive_choice"]

        if not motive_choice:
            return {
                "valid": False,
                "message": "No motive was established."
            }

        correct_motive = "Evidence tampering to conceal access"

        if motive_choice == correct_motive:
            return {
                "valid": True,
                "message": "The motive is consistent with Sophie's attempt to conceal her involvement."
            }

        return {
            "valid": False,
            "message": "The selected motive does not best explain Sophie's actions."
        }

    def analyze_evidence_support(self, theory):
        """Analyze if evidence choices support the theory"""
        selected_count = len(theory["evidence_ids"])
        investigated_count = len(self.investigated_evidence)
        
        correct_solution = self.resolution_config["correct_solution"]
        required_evidence = set(correct_solution["supporting_evidence_ids"])
        has_required = len(theory["evidence_ids"] & required_evidence)
        
        if selected_count < 2:
            return {"valid": False, "message": "Insufficient evidence was selected to support your theory.", "count": selected_count}
        
        if has_required >= correct_solution["required_evidence_count"]:
            return {"valid": True, "message": f"{selected_count} pieces of evidence selected, including critical connections.", "count": selected_count}
        else:
            return {
                "valid": False,
                "message": "Critical evidence connections are missing from your selection.",
                "count": selected_count
            }

    def show_theory_analysis(self, results):
        """Show the analysis modal with colour-coded results."""

        # DARK BACKGROUND OVERLAY

        overlay = ctk.CTkFrame(
            self,
            fg_color="#000000",
            corner_radius=0
        )

        overlay.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        # MAIN MODAL

        modal = ctk.CTkFrame(
            overlay,
            width=720,
            height=650,
            fg_color=self.theme["card"],
            corner_radius=18,
            border_width=1,
            border_color=self.theme["border"]
        )

        modal.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        modal.pack_propagate(False)

        # HEADER

        header = ctk.CTkLabel(
            modal,
            text="ANALYZING CASE THEORY...",
            font=("Arial", 24, "bold"),
            text_color=self.theme["heading"]
        )

        header.pack(
            pady=(32, 8)
        )

        subtitle = ctk.CTkLabel(
            modal,
            text="Reviewing your conclusions against the available evidence",
            font=("Arial", 13),
            text_color=self.theme["muted"]
        )

        subtitle.pack(
            pady=(0, 20)
        )

        # RESULT COLOURS

        correct_color = "#22C55E"
        correct_bg = "#102B1B"

        incorrect_color = "#FF3B3B"
        incorrect_bg = "#321515"

        # CHECK OVERALL RESULT

        required_categories = [
            "suspect",
            "timeline",
            "method",
            "motive",
            "evidence"
        ]

        all_valid = all(
            results[key]["valid"]
            for key in required_categories
            if key in results
        )

        # RESULT ROWS

        categories = [
            ("suspect", "SUSPECT"),
            ("timeline", "TIMELINE"),
            ("method", "METHOD"),
            ("motive", "MOTIVE"),
            ("evidence", "SUPPORTING EVIDENCE")
        ]

        for key, title in categories:

            if key not in results:
                continue

            result = results[key]

            is_correct = result["valid"]

            accent_color = (
                correct_color
                if is_correct
                else incorrect_color
            )

            background_color = (
                correct_bg
                if is_correct
                else incorrect_bg
            )

            symbol = "✓" if is_correct else "✕"

            status_text = (
                "CORRECT"
                if is_correct
                else "INCORRECT"
            )


            # Main result card
            result_frame = ctk.CTkFrame(
                modal,
                height=58,
                fg_color=background_color,
                corner_radius=10,
                border_width=1,
                border_color=accent_color
            )

            result_frame.pack(
                fill="x",
                padx=30,
                pady=4
            )

            result_frame.pack_propagate(False)


            # Left side
            left_frame = ctk.CTkFrame(
                result_frame,
                fg_color="transparent"
            )

            left_frame.pack(
                side="left",
                fill="y",
                padx=18
            )


            symbol_label = ctk.CTkLabel(
                left_frame,
                text=symbol,
                font=("Arial", 24, "bold"),
                text_color=accent_color,
                width=30
            )

            symbol_label.pack(
                side="left",
                padx=(0, 10)
            )


            title_label = ctk.CTkLabel(
                left_frame,
                text=title,
                font=("Arial", 14, "bold"),
                text_color=accent_color
            )

            title_label.pack(
                side="left"
            )


            # Right side
            right_frame = ctk.CTkFrame(
                result_frame,
                fg_color="transparent"
            )

            right_frame.pack(
                side="right",
                fill="y",
                padx=18
            )


            status_label = ctk.CTkLabel(
                right_frame,
                text=status_text,
                font=("Arial", 11, "bold"),
                text_color=accent_color
            )

            status_label.pack(
                side="top",
                anchor="e",
                pady=(8, 0)
            )


            # For evidence, show selected count
            if key == "evidence":

                detail = (
                    f"{result.get('count', 0)} evidence selected"
                )

            else:

                detail = result.get(
                    "message",
                    ""
                )


            detail_label = ctk.CTkLabel(
                right_frame,
                text=detail,
                font=("Arial", 10),
                text_color=self.theme["text"],
                wraplength=300,
                justify="right"
            )

            detail_label.pack(
                side="top",
                anchor="e"
            )

        # SUMMARY

        correct_count = sum(
            1
            for key in required_categories
            if key in results and results[key]["valid"]
        )

        incorrect_count = len(
            [
                key
                for key in required_categories
                if key in results and not results[key]["valid"]
            ]
        )


        summary_frame = ctk.CTkFrame(
            modal,
            fg_color="transparent"
        )

        summary_frame.pack(
            pady=(15, 12)
        )


        correct_label = ctk.CTkLabel(
            summary_frame,
            text=f"✓ {correct_count} CORRECT",
            font=("Arial", 14, "bold"),
            text_color=correct_color
        )

        correct_label.pack(
            side="left",
            padx=20
        )


        incorrect_label = ctk.CTkLabel(
            summary_frame,
            text=f"✕ {incorrect_count} INCORRECT",
            font=("Arial", 14, "bold"),
            text_color=incorrect_color
        )

        incorrect_label.pack(
            side="left",
            padx=20
        )

        # FINAL MESSAGE

        if all_valid:

            message = (
                "Your theory is fully supported by the evidence."
            )

            message_color = correct_color

        else:

            message = (
                "Your theory has gaps. Revisit the evidence "
                "and investigate the connections you may have missed."
            )

            message_color = self.theme["muted"]


        feedback_label = ctk.CTkLabel(
            modal,
            text=message,
            font=("Arial", 12),
            text_color=message_color,
            wraplength=600,
            justify="center"
        )

        feedback_label.pack(
            padx=40,
            pady=(0, 15)
        )

        # ACTION BUTTON

        if all_valid:

            action_button = ctk.CTkButton(
                modal,
                text="CLOSE CASE  →",
                width=240,
                height=46,
                font=("Arial", 14, "bold"),
                corner_radius=10,
                fg_color=correct_color,
                hover_color="#16A34A",
                text_color="#FFFFFF",
                command=lambda: self.complete_case(overlay)
            )

        else:

            action_button = ctk.CTkButton(
                modal,
                text="CONTINUE INVESTIGATION  →",
                width=260,
                height=46,
                font=("Arial", 14, "bold"),
                corner_radius=10,
                fg_color=self.theme["primary"],
                hover_color=self.theme["primary_hover"],
                text_color=self.theme["heading"],
                command=overlay.destroy
            )


        action_button.pack(
            pady=(0, 25)
        )

    def complete_case(self, overlay):

        self.case_closed = True
        self.resolution_unlocked = True

        # Close the theory analysis modal
        overlay.destroy()

        # Save progress if you have a save function
        if hasattr(self, "save_game_state"):
            self.save_game_state()

        # CASE CLOSED OVERLAY

        congrats_overlay = ctk.CTkFrame(
            self,
            fg_color="#000000",
            corner_radius=0
        )

        congrats_overlay.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        # CONGRATULATIONS CARD

        congrats_card = ctk.CTkFrame(
            congrats_overlay,
            width=700,
            height=480,
            fg_color=self.theme["card"],
            corner_radius=20,
            border_width=1,
            border_color="#22C55E"
        )

        congrats_card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        congrats_card.pack_propagate(False)

        # CASE CLOSED LABEL

        closed_label = ctk.CTkLabel(
            congrats_card,
            text="CASE CLOSED",
            font=("Arial", 14, "bold"),
            text_color="#22C55E"
        )

        closed_label.pack(
            pady=(55, 8)
        )

        # MAIN TITLE

        title = ctk.CTkLabel(
            congrats_card,
            text="CONGRATULATIONS, DETECTIVE.",
            font=("Arial", 28, "bold"),
            text_color=self.theme["heading"]
        )

        title.pack(
            pady=(0, 18)
        )

        # MESSAGE

        message = ctk.CTkLabel(
            congrats_card,
            text=(
                "Your investigation connected the evidence, exposed "
                "the contradictions, and reconstructed what happened "
                "during the critical security window."
            ),
            font=("Arial", 14),
            text_color=self.theme["text"],
            wraplength=560,
            justify="center"
        )

        message.pack(
            padx=50,
            pady=(0, 25)
        )

        # DIVIDER

        divider = ctk.CTkFrame(
            congrats_card,
            height=1,
            fg_color=self.theme["border"]
        )

        divider.pack(
            fill="x",
            padx=70,
            pady=(0, 22)
        )

        # FINAL MESSAGE

        final_label = ctk.CTkLabel(
            congrats_card,
            text="CASE #042 SUCCESSFULLY RESOLVED",
            font=("Arial", 13, "bold"),
            text_color="#22C55E"
        )

        final_label.pack(
            pady=(0, 30)
        )

        # RETURN BUTTON

        def finish_case():

            congrats_overlay.destroy()

            self.show_case_summary()


        finish_button = ctk.CTkButton(
            congrats_card,
            text="VIEW CASE SUMMARY  →",
            width=240,
            height=46,
            font=("Arial", 14, "bold"),
            corner_radius=10,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#FFFFFF",
            command=finish_case
        )

        finish_button.pack()

    def show_case_closed_state(self):
        """Show the case closed state"""
        closed_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        closed_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        # Case closed badge
        badge = ctk.CTkLabel(
            closed_frame,
            text="🔒 CASE CLOSED",
            font=("Arial", 24, "bold"),
            text_color=self.theme["warning"]
        )
        badge.pack(
            pady=(40, 15)
        )

        case_number = ctk.CTkLabel(
            closed_frame,
            text="CASE #042 — RESOLVED",
            font=("Arial", 18, "bold"),
            text_color=self.theme["heading"]
        )
        case_number.pack(
            pady=(0, 25)
        )

        # Statistics
        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        stats_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        stats_title = ctk.CTkLabel(
            stats_frame,
            text="INVESTIGATION STATISTICS",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        )
        stats_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 15)
        )

        # Calculate statistics
        stats = [
            f"Evidence Discovered: {len(self.investigated_evidence)}",
            f"Evidence Connections Made: {len(self.discovered_leads)}",
            f"Timeline Events Reconstructed: {len(self.get_resolved_timeline_events())}",
            f"Contradictions Exposed: {sum(1 for c in self.contradictions.values() if c['deduction_id'] in self.discovered_leads)}",
            f"Interview Questions Asked: {self.get_total_asked_questions()}"
        ]

        for stat in stats:
            stat_label = ctk.CTkLabel(
                stats_frame,
                text=stat,
                font=("Arial", 13),
                text_color=self.theme["text"],
                anchor="w"
            )
            stat_label.pack(
                anchor="w",
                padx=20,
                pady=(0, 8)
            )

        # Resolution summary
        summary_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card"],
            corner_radius=12
        )
        summary_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 20)
        )

        summary_title = ctk.CTkLabel(
            summary_frame,
            text="CASE RESOLUTION SUMMARY",
            font=("Arial", 13, "bold"),
            text_color=self.theme["accent"]
        )
        summary_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 15)
        )

        correct_solution = self.resolution_config["correct_solution"]
        
        # Get suspect name
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suspects WHERE id = %s", (correct_solution["suspect_id"],))
        suspect = cursor.fetchone()
        cursor.close()
        connection.close()

        summary_text = ctk.CTkLabel(
            summary_frame,
            text=f"Sophie Laurent was identified as responsible through security administrator credentials, executive floor access during the blackout, and physical evidence placing her at the scene. The coordinated timing of the security override, access card usage, and camera blackout established a deliberate concealment effort.",
            font=("Arial", 13),
            text_color=self.theme["text"],
            justify="left",
            wraplength=800,
            anchor="w"
        )
        summary_text.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    def show_case_summary(self):

        # CLEAR THE ENTIRE WINDOW

        for widget in self.winfo_children():
            widget.destroy()

        # FULL SCREEN BACKGROUND

        summary_page = ctk.CTkFrame(
            self,
            fg_color=self.theme["background"],
            corner_radius=0
        )

        summary_page.pack(
            fill="both",
            expand=True
        )

        # CONTENT CONTAINER

        content = ctk.CTkFrame(
            summary_page,
            fg_color="transparent"
        )

        content.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.72,
            relheight=0.88
        )

        # CASE CLOSED LABEL

        case_closed_label = ctk.CTkLabel(
            content,
            text="CASEFILE / CASE CLOSED",
            font=("Arial", 13, "bold"),
            text_color="#22C55E"
        )

        case_closed_label.pack(
            anchor="w",
            pady=(10, 8)
        )

        # TITLE

        title = ctk.CTkLabel(
            content,
            text="What Really Happened",
            font=("Arial", 38, "bold"),
            text_color=self.theme["heading"]
        )

        title.pack(
            anchor="w"
        )


        subtitle = ctk.CTkLabel(
            content,
            text=(
                "The investigation revealed how the murder was concealed "
                "and why the evidence pointed to Sophie Laurent."
            ),
            font=("Arial", 15),
            text_color=self.theme["muted"],
            wraplength=850,
            justify="left"
        )

        subtitle.pack(
            anchor="w",
            pady=(10, 28)
        )

        # DIVIDER

        divider = ctk.CTkFrame(
            content,
            height=1,
            fg_color=self.theme["border"]
        )

        divider.pack(
            fill="x",
            pady=(0, 25)
        )

        # SUMMARY POINTS    

        summary_points = [

            (
                "01",
                "The confrontation",
                (
                    "Sophie Laurent had a strong reason to confront the victim. "
                    "The victim had discovered that security access logs had been "
                    "altered under her credentials, placing Sophie's position and "
                    "career at serious risk."
                )
            ),

            (
                "02",
                "The cameras were disabled",
                (
                    "At 10:10 PM, the executive floor CCTV system was manually "
                    "overridden using security administrator access. The cameras "
                    "remained offline until 10:28 PM, creating a window in which "
                    "the confrontation could take place without being recorded."
                )
            ),

            (
                "03",
                "Sophie was inside the victim's office",
                (
                    "A second coffee cup recovered from the victim's office "
                    "contained traces of Sophie's lipstick. This directly placed "
                    "her in the office and contradicted the idea that she remained "
                    "only in the security office reviewing footage."
                )
            ),

            (
                "04",
                "The struggle occurred during the blackout",
                (
                    "The victim's broken watch stopped at approximately 10:24 PM. "
                    "This placed the struggle directly inside the CCTV blackout, "
                    "at a time when the executive floor was deliberately left "
                    "without camera coverage."
                )
            ),

            (
                "05",
                "Other suspects were eliminated",
                (
                    "Noah Bennett was confirmed by CCTV to be inside the server "
                    "room during the estimated time of the struggle. Marcus Reid's "
                    "alibi was inconsistent, but the available evidence did not "
                    "place him at the crime scene. Elena's access card created "
                    "suspicion, but it did not establish that she committed the murder."
                )
            ),

            (
                "06",
                "The conclusion",
                (
                    "The strongest combination of motive, opportunity, physical "
                    "presence, and control over the CCTV system pointed to Sophie "
                    "Laurent. She used her access to create the security blackout, "
                    "confronted the victim, and the confrontation turned deadly."
                )
            )

        ]

        # CREATE SUMMARY CARDS        

        for number, heading, description in summary_points:

            point_frame = ctk.CTkFrame(
                content,
                fg_color=self.theme["card"],
                corner_radius=12,
                border_width=1,
                border_color=self.theme["border"]
            )

            point_frame.pack(
                fill="x",
                pady=6
            )

            # Number

            number_label = ctk.CTkLabel(
                point_frame,
                text=number,
                font=("Arial", 16, "bold"),
                text_color="#22C55E",
                width=55
            )

            number_label.pack(
                side="left",
                padx=(20, 12),
                pady=16
            )

            # Text container

            text_container = ctk.CTkFrame(
                point_frame,
                fg_color="transparent"
            )

            text_container.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 25),
                pady=14
            )


            heading_label = ctk.CTkLabel(
                text_container,
                text=heading,
                font=("Arial", 15, "bold"),
                text_color=self.theme["heading"],
                anchor="w"
            )

            heading_label.pack(
                anchor="w"
            )


            description_label = ctk.CTkLabel(
                text_container,
                text=description,
                font=("Arial", 12),
                text_color=self.theme["text"],
                wraplength=800,
                justify="left",
                anchor="w"
            )

            description_label.pack(
                anchor="w",
                pady=(5, 0)
            )

        # FINAL DIVIDER

        bottom_divider = ctk.CTkFrame(
            content,
            height=1,
            fg_color=self.theme["border"]
        )

        bottom_divider.pack(
            fill="x",
            pady=(25, 15)
        )

        # FINAL STATUS

        solved_label = ctk.CTkLabel(
            content,
            text="CASE #042  •  RESOLVED",
            font=("Arial", 13, "bold"),
            text_color="#22C55E"
        )

        solved_label.pack(
            anchor="w"
        )

        # RETURN BUTTON

        return_button = ctk.CTkButton(
            content,
            text="RETURN TO CASEFILE  →",
            width=220,
            height=44,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            text_color=self.theme["heading"],
            command=self.restart_casefile_interface
        )

        return_button.pack(
            anchor="w",
            pady=(15, 10)
        )

    def restart_casefile_interface(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.create_layout()

        self.show_page("case resolution")

if __name__ == "__main__":
    app = CaseFileApp()
    app.mainloop()