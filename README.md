# CASEFILE

An interactive desktop detective game built with **Python, CustomTkinter, and MySQL**.

CASEFILE places the player in charge of investigating a murder inside a company's executive and security infrastructure. The player must examine evidence, investigate suspects, uncover contradictions, connect related pieces of information, reconstruct the timeline, and ultimately submit a complete theory explaining the case.

The investigation is designed to be solved through reasoning rather than simply selecting random answers.

---

## Overview

A critical incident has occurred within the company's executive infrastructure.

Several individuals have possible motives. Security records contain inconsistencies. Important evidence is scattered across multiple systems, and witness statements do not form a complete timeline.

The player takes the role of an investigator and must determine:

- Who was responsible
- When the critical events occurred
- How the crime was concealed
- What motive explains the suspect's actions
- Which pieces of evidence support the final theory

The investigation gradually progresses as the player explores evidence and discovers connections.

---

# Features

## Case Briefing

When the application starts, the player is presented with an animated case briefing.

The briefing introduces:

- The nature of the incident
- The incomplete state of the evidence
- The investigation objectives
- The individuals connected to the case

The briefing can also be reopened later from the sidebar.

---

## Suspect Investigation

The game contains multiple suspects connected to the incident.

Each suspect has information including:

- Name
- Age
- Occupation
- Possible motive
- Alibi
- Investigation status

Players can inspect individual suspect profiles and ask investigation questions.

Some questions are initially locked and become available only after the player discovers specific findings.

This allows the investigation to progress naturally instead of presenting all information immediately.

---

## Evidence System

The evidence section contains multiple pieces of evidence collected from different locations and systems.

Evidence can include:

- Digital records
- Security logs
- CCTV information
- Physical evidence
- Financial records
- Access card activity
- Meeting records

Each evidence item contains information such as:

- Title
- Description
- Evidence type
- Location
- Importance level

Players can investigate evidence to uncover additional information.

---

## Evidence Connections

One of the core mechanics of CASEFILE is the ability to connect related pieces of evidence.

The game contains predefined valid evidence combinations.

For example, connecting related evidence may reveal:

- Suspicious timing
- Contradictory alibis
- Security system manipulation
- Physical presence at a location
- Connections between suspects and events

Successful connections generate new findings.

These findings become part of the player's investigation progress.

---

## Investigation Findings

Discovered information is collected on the **Case Findings** page.

This page acts as a deduction board containing:

- Important discoveries
- Evidence connections
- Contradictions
- Timeline relationships
- Suspect-related findings

The player gradually builds a clearer understanding of the case as more findings are discovered.

---

## Dynamic Interview Questions

Not every question is available immediately.

Some questions require the player to discover specific findings first.

For example, discovering a contradiction or connecting two pieces of evidence may unlock a new question for a suspect.

This creates a progression system:

```
Investigate Evidence
        ↓
Discover Information
        ↓
Connect Evidence
        ↓
Unlock Findings
        ↓
Unlock New Questions
        ↓
Expose Contradictions
        ↓
Advance the Investigation