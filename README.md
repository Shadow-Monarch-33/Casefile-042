# CASEFILE #42

### Every suspect has a story. Every piece of evidence tells another.

**CASEFILE #42** is an interactive desktop detective game built using **Python, CustomTkinter, and SQLite**, where players investigate a fictional murder by examining evidence, interrogating suspects, identifying contradictions, and reconstructing the events surrounding the crime.

Rather than relying on random guesses, players must build a case through observation, deduction, and logical reasoning.

The truth is hidden in the evidence. Your job is to connect it.

---

## The Case

A company executive has been found dead inside his office at approximately **11:05 PM**.

Four individuals are connected to the investigation. Each has a possible motive, an alibi, and information they may not be telling you.

The company's security infrastructure raises further questions. Surveillance footage is missing, access records contain suspicious activity, and witness statements do not entirely agree with the available evidence.

As the investigator, you must determine:

- Who was responsible for the murder?
- What happened during the critical period?
- Which suspects are concealing information?
- How was the crime carried out and concealed?
- What evidence supports your final conclusion?

**There is one case to solve, but multiple leads to investigate.**

---

## Features

### Interactive Suspect Interviews

Investigate four suspects, each with their own background, possible motive, and alibi.

Ask questions, examine their statements, and confront them with evidence. Suspects respond differently depending on the evidence presented.

New interview questions become available as you uncover important findings.

### Evidence Investigation

Explore a collection of physical, digital, and documentary evidence, including security records, surveillance footage, financial documents, and objects recovered from the crime scene.

Every item has a role in the investigation, but its significance may not be immediately obvious.

### Evidence Connections & Deduction

Analyze relationships between different pieces of evidence to discover new findings.

Connecting relevant evidence can reveal:

- Contradictory timelines
- Suspicious security activity
- Inconsistencies in suspect statements
- Previously unnoticed relationships
- New investigative leads

Not every combination produces a meaningful discovery.

### Dynamic Timeline

Reconstruct the events leading up to the murder.

The timeline develops as new information is uncovered, gradually replacing uncertainty with a clearer sequence of events.

### Contradiction Detection

Challenge suspect statements using the evidence you've collected.

Presenting the right evidence against a conflicting statement can expose contradictions and unlock additional investigative opportunities.

### Case Findings Board

All discovered findings are collected in a dedicated investigation view.

Review connections, contradictions, and deductions to understand how the different parts of the case fit together.

### Contextual Hint System

Stuck on an investigation?

CASEFILE includes a limited hint system that provides guidance based on your current progress without immediately revealing the solution.

### Final Case Resolution

Once enough critical findings have been discovered, the final resolution becomes available.

Players must construct a theory supported by the investigation rather than simply guessing a suspect.

### Customizable Themes

Choose between four visual themes:

- Midnight Blue
- Crimson Noir
- Emerald Investigation
- Monochrome

---

## Screenshots

*Add screenshots of the actual application here.*

Recommended screenshots:

- Case Overview
- Evidence Investigation
- Suspect Interviews
- Case Findings Board

---

## How the Investigation Works

```text
Explore the Case
       |
       v
Examine Evidence
       |
       v
Interview Suspects
       |
       v
Connect Related Evidence
       |
       v
Discover New Findings
       |
       v
Unlock Questions & Timeline Events
       |
       v
Expose Contradictions
       |
       v
Build and Submit Your Theory
```

Progression is discovery-driven. Players can investigate different leads and gradually develop an understanding of the case.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and game logic |
| CustomTkinter | Desktop graphical interface |
| SQLite (Python standard library) | Local storage of suspects, evidence, timelines, and relationships |

---

## Getting Started

### Prerequisites

Before running CASEFILE, make sure you have:

- Python 3.10 or newer
- A desktop environment supporting Tkinter
- Git (optional, for cloning)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the placeholders with the repository's actual URL and directory name.

### 2. Create a Virtual Environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages are:

```text
customtkinter
```

### 4. Database Configuration

No configuration is needed. CASEFILE uses Python's built-in SQLite library.
The file `casefile.db` is created in the project directory when you initialize the database.
It is excluded from Git so your local game data stays on your computer.

### 5. Initialize the Database

```bash
python setup_database.py
```

This creates the required tables and populates the initial case data.

The setup script is designed to avoid overwriting existing case records when run again.
An existing MySQL database is **not** migrated automatically; only the original case seed is created.

### 6. Launch CASEFILE

```bash
python app.py
```

The desktop application will open with the initial case briefing.

You can now begin investigating.

---

## Project Structure

```text
CASEFILE/
├── app.py
├── database.py
├── setup_database.py
├── requirements.txt
├── casefile.db         # Created locally when initialized (ignored by Git)
├── .gitignore
├── README.md
└── screenshots/       # Optional screenshots
```

**app.py** — Main application, interface, and investigation mechanics.

**database.py** — Local SQLite connection configuration.

**setup_database.py** — Database schema creation and initial case data.

**requirements.txt** — Python dependencies.

---

## Current Limitations

CASEFILE is currently a single-case desktop game.

- The investigation contains one playable murder mystery.
- Investigation progress is stored in memory during the application session and is not currently saved between launches.
- The application has not been packaged as a standalone executable.

These limitations reflect the current scope of the project.

---

## Future Improvements

Potential improvements include:

- Persistent investigation progress and save slots
- Additional cases with different suspects and evidence
- Separation of case content from the application logic
- More advanced deduction mechanics
- Standalone desktop builds
- Automated testing of investigation progression

---

## About the Project

CASEFILE #42 was created as a Python desktop application project exploring how databases, graphical interfaces, and interconnected game logic can work together.

The project focuses on making information meaningful through interaction. Database records are not simply displayed; players must interpret them, discover relationships, and use those relationships to progress through the investigation.

It combines relational database design, Python programming, interface development, and branching investigative gameplay into a single application.

---

**CASEFILE #42 —> Follow the evidence. Question everything.**
