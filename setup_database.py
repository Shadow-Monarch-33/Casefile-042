from database import get_connection


def setup_database():
    connection = None
    cursor = None

    try:
        connection = get_connection(use_database=False)
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS casefile")
        cursor.execute("USE casefile")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suspects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT,
                occupation VARCHAR(100),
                motive TEXT,
                alibi TEXT,
                status VARCHAR(50) DEFAULT 'Under Investigation'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                description TEXT NOT NULL,
                evidence_type VARCHAR(50),
                location VARCHAR(100),
                importance ENUM(
                    'Low', 'Medium', 'High', 'Critical'
                ) DEFAULT 'Medium'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_time TIME NOT NULL,
                event VARCHAR(255) NOT NULL,
                location VARCHAR(100) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_connections (
                evidence_id INT NOT NULL,
                suspect_id INT NOT NULL,
                connection_description TEXT,

                PRIMARY KEY (evidence_id, suspect_id),

                FOREIGN KEY (evidence_id)
                    REFERENCES evidence(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (suspect_id)
                    REFERENCES suspects(id)
                    ON DELETE CASCADE
            )
        """)
        
        tables = (
            "suspects",
            "evidence",
            "timeline",
            "evidence_connections",
        )

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            if cursor.fetchone()[0] > 0:
                print(
                    "Existing case data detected. "
                    "Skipping seed operation."
                )
                print("Database 'casefile' is ready.")
                return

        for table in ("suspects", "evidence"):
            cursor.execute(f"SHOW TABLE STATUS LIKE '{table}'")
            status = cursor.fetchone()
            if status is not None:
                next_id = status[10]
                if next_id is not None and next_id != 1:
                    raise RuntimeError(
                        f"Table '{table}' has an existing ID sequence. "
                        "Use a fresh database for the initial case seed."
                    )

        suspects = [
            (
                "Elena Vasquez",
                34,
                "Co-Founder & CTO",
                "The victim planned to remove her from the company after discovering she had leaked confidential source code.",
                "Claims she left the office at 9:40 PM and went home.",
                "Under Investigation"
            ),
            (
                "Marcus Reid",
                41,
                "Chief Financial Officer",
                "The victim had recently discovered unexplained transfers from the company's accounts.",
                "Claims he was in a meeting with investors from 9:00 PM to 10:30 PM.",
                "Under Investigation"
            ),
            (
                "Noah Bennett",
                29,
                "Lead Software Engineer",
                "The victim rejected his request for equity in the company and planned to terminate his project.",
                "Claims he was working alone in the server room until 10:45 PM.",
                "Under Investigation"
            ),
            (
                "Sophie Laurent",
                37,
                "Head of Security",
                "The victim had discovered that security access logs had been altered under her credentials.",
                "Claims she was reviewing CCTV footage in the security office during the estimated time of death.",
                "Under Investigation"
            )
        ]

        evidence = [
            (
                "Access Card Log",
                "An access card registered to Elena Vasquez was used to enter the executive floor at 10:12 PM.",
                "Digital",
                "Executive Floor",
                "High"
            ),
            (
                "Deleted Financial Records",
                "Several transaction records connected to Marcus Reid were deleted shortly before the murder.",
                "Digital",
                "Finance Server",
                "High"
            ),
            (
                "Server Room Camera",
                "CCTV footage confirms Noah Bennett remained inside the server room from 10:05 PM to 10:47 PM.",
                "Digital",
                "Server Room",
                "Critical"
            ),
            (
                "Security Camera Gap",
                "The CCTV system stopped recording the executive floor between 10:10 PM and 10:28 PM due to a manual override.",
                "Digital",
                "Security System",
                "Critical"
            ),
            (
                "Broken Watch",
                "The victim's broken watch stopped at 10:24 PM, suggesting the approximate time of the struggle.",
                "Physical",
                "Victim's Office",
                "High"
            ),
            (
                "Investor Meeting Record",
                "The scheduled investor meeting attended by Marcus Reid ended at 10:08 PM, contradicting his claim that it continued until 10:30 PM.",
                "Document",
                "Conference Room",
                "High"
            ),
            (
                "Security Console Login",
                "A security administrator account was used to manually override the CCTV system at 10:10 PM.",
                "Digital",
                "Security Office",
                "Critical"
            ),
            (
                "Coffee Cup",
                "A second coffee cup found in the victim's office contained traces of Sophie Laurent's lipstick.",
                "Physical",
                "Victim's Office",
                "Medium"
            ),
            (
                "Security Workstation Activity",
                "System activity records show that the security administrator session initiated at 10:09 PM originated from terminal SEC-03. Company asset records assign SEC-03 to Sophie Laurent for routine security administration duties.",
                "Digital",
                "Security Office",
                "Critical"
            )
        ]

        timeline = [
            (
                "21:40:00",
                "Elena Vasquez leaves the executive floor and claims to go home.",
                "Executive Floor"
            ),
            (
                "22:05:00",
                "Noah Bennett enters the server room.",
                "Server Room"
            ),
            (
                "22:08:00",
                "Marcus Reid's investor meeting officially ends.",
                "Conference Room"
            ),
            (
                "22:10:00",
                "The executive floor CCTV system is manually overridden.",
                "Security System"
            ),
            (
                "22:12:00",
                "An access card registered to Elena is used on the executive floor.",
                "Executive Floor"
            ),
            (
                "22:24:00",
                "A struggle is believed to have occurred in the victim's office based on the broken watch.",
                "Victim's Office"
            ),
            (
                "22:28:00",
                "The executive floor CCTV system resumes recording.",
                "Security System"
            ),
            (
                "22:47:00",
                "Noah Bennett leaves the server room.",
                "Server Room"
            ),
            (
                "23:05:00",
                "The victim is found dead inside his office.",
                "Victim's Office"
            )
        ]

        evidence_connections = [
            (
                1, 1,
                "Elena's access card was used on the executive floor at 10:12 PM."
            ),
            (
                2, 2,
                "Deleted financial records are connected to transactions handled by Marcus."
            ),
            (
                3, 3,
                "Camera footage confirms Noah's location during the estimated time of death."
            ),
            (
                4, 4,
                "The CCTV override requires security-level access connected to Sophie's department."
            ),
            (
                6, 2,
                "The meeting record contradicts Marcus's alibi."
            ),
            (
                7, 4,
                "A security administrator account was used to override the CCTV system."
            ),
            (
                8, 4,
                "Sophie's lipstick was found on a coffee cup inside the victim's office."
            ),
            (
                5, 1,
                "The broken watch places the estimated time of the struggle at 10:24 PM, after Elena claimed she had already gone home."
            ),
            (
                5, 2,
                "Marcus's whereabouts at the estimated time of the struggle are unverified after his investor meeting ended."
            ),
            (
                5, 3,
                "The estimated time of the struggle falls within the period Noah is confirmed by CCTV to have been in the server room."
            ),
            (
                5, 4,
                "The estimated time of the struggle occurred during the CCTV blackout linked to security-level access."
            ),
            (
                4, 1,
                "Elena's access card was used on the executive floor shortly after the CCTV system was manually overridden."
            )
        ]
        
        cursor.executemany("""
            INSERT INTO suspects
            (name, age, occupation, motive, alibi, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, suspects)

        cursor.executemany("""
            INSERT INTO evidence
            (title, description, evidence_type, location, importance)
            VALUES (%s, %s, %s, %s, %s)
        """, evidence)

        cursor.executemany("""
            INSERT INTO timeline
            (event_time, event, location)
            VALUES (%s, %s, %s)
        """, timeline)

        cursor.executemany("""
            INSERT INTO evidence_connections
            (evidence_id, suspect_id, connection_description)
            VALUES (%s, %s, %s)
        """, evidence_connections)

        connection.commit()

        print("Database 'casefile' initialized successfully!")
        print(f"Suspects: {len(suspects)}")
        print(f"Evidence items: {len(evidence)}")
        print(f"Timeline events: {len(timeline)}")
        print(f"Evidence connections: {len(evidence_connections)}")
        print("CASEFILE #42 is ready.")

    except Exception as error:
        if connection is not None:
            connection.rollback()
        print(f"Database setup failed: {error}")
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    setup_database()
