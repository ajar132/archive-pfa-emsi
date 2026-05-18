from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(21, 96, 130)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Archive Digitale PFA  --  Technical Breakdown",
                  fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()} / {{nb}}", align="C")

    def h1(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(21, 96, 130)
        self.set_text_color(255, 255, 255)
        self.cell(0, 9, text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def h2(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(21, 96, 130)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(21, 96, 130)
        self.set_line_width(0.4)
        self.line(self.get_x(), self.get_y(), self.get_x() + 170, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=5):
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin + indent)
        self.multi_cell(0, 5.5, f"-  {text}")

    def code(self, text):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(240, 244, 248)
        self.set_x(self.l_margin + 5)
        self.multi_cell(0, 5, text, fill=True)
        self.set_font("Helvetica", "", 10)
        self.ln(1)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            w = 170 // len(headers)
            col_widths = [w] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(21, 96, 130)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7, h, border=1, fill=True, align="C")
        self.ln()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(235, 245, 250)
            else:
                self.set_fill_color(255, 255, 255)
            for cell, w in zip(row, col_widths):
                self.cell(w, 6, cell, border=1, fill=True)
            self.ln()
        self.ln(2)


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title block
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(21, 96, 130)
pdf.ln(8)
pdf.cell(0, 12, "Archive Digitale PFA", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Technical Breakdown  --  Full Project Analysis",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(6)

# 1. PROJECT ARCHITECTURE
pdf.h1("1. Project Architecture")
pdf.body(
    "The project follows a clean two-layer architecture: a backend service layer (src/) "
    "and a GUI presentation layer (gui/), connected through direct Python imports "
    "(no HTTP, no event bus, no message queue)."
)

pdf.h2("Directory Structure")
pdf.code(
    "archive_pfa/\n"
    "|-- main.py                   <- DB bootstrap + seed accounts\n"
    "|-- database/\n"
    "|   +-- archive.db            <- SQLite file (single source of truth)\n"
    "|-- storage/\n"
    "|   +-- rapports/             <- Physical PDF files on disk\n"
    "|-- src/                      <- Backend (pure logic, no UI)\n"
    "|   |-- database.py           <- Connection factory + DDL (CREATE TABLE)\n"
    "|   |-- crud.py               <- All DB reads/writes\n"
    "|   |-- security.py           <- bcrypt hashing\n"
    "|   +-- pdf_handler.py        <- PDF copy, text extraction, similarity\n"
    "+-- gui/                      <- PyQt5 windows (pure UI)\n"
    "    |-- login_window.py\n"
    "    |-- main_window.py        <- Shell: sidebar nav + QStackedWidget\n"
    "    |-- depot_window.py       <- Report submission form\n"
    "    |-- evaluation_window.py  <- Encadrant grading workflow\n"
    "    |-- recherche_window.py   <- Multi-criteria search\n"
    "    |-- dashboard_window.py   <- Statistics + pie chart\n"
    "    |-- preview_window.py     <- Inline PDF viewer\n"
    "    +-- users_window.py       <- Admin user CRUD"
)
pdf.body(
    "Note: main.py is NOT the application launcher -- it is a DB initializer/seeder. "
    "The actual GUI entry point is:  python -m gui.login_window"
)

# 2. CORE FUNCTIONALITY
pdf.h1("2. Core Functionality")
pdf.body(
    "This is a desktop digital archive system for managing student end-of-year project "
    "reports (PFAs) at EMSI (Ecole Marocaine des Sciences de l'Ingenieur)."
)
pdf.table(
    ["Feature", "Description"],
    [
        ["Secure login",         "Email + bcrypt-hashed password, 3-attempt lockout"],
        ["RBAC",                 "3 roles with different menu visibility and data access"],
        ["Report submission",    "PDF upload + metadata form + automatic plagiarism check"],
        ["Plagiarism detection", "TF-IDF + cosine similarity vs. all existing reports"],
        ["Evaluation workflow",  "Encadrant reviews, grades, accepts or rejects reports"],
        ["Search",               "Multi-criteria keyword/year search, role-filtered results"],
        ["PDF preview",          "Inline viewer with page navigation and zoom slider"],
        ["Dashboard",            "Real-time stats cards + matplotlib pie chart"],
        ["User management",      "Admin creates/edits/deletes all accounts"],
    ],
    col_widths=[55, 115]
)

# 3. TECHNOLOGY STACK
pdf.h1("3. Technology Stack")
pdf.table(
    ["Layer", "Technology", "Purpose"],
    [
        ["Language",  "Python 3.13",         "Entire application"],
        ["GUI",       "PyQt5",               "All windows, forms, tables, dialogs"],
        ["Database",  "SQLite 3",            "Embedded relational DB via sqlite3 stdlib"],
        ["Security",  "bcrypt",              "Salted password hashing"],
        ["PDF",       "PyMuPDF (fitz)",      "Text extraction + page rendering to pixmap"],
        ["ML / NLP",  "scikit-learn",        "TfidfVectorizer + cosine_similarity"],
        ["Charts",    "Matplotlib Qt5Agg",   "Pie chart embedded as Qt widget"],
    ],
    col_widths=[35, 55, 80]
)

# 4. DATA FLOW
pdf.h1("4. Data Flow")

pdf.h2("4.1  Authentication Flow")
pdf.code(
    "User types email + password\n"
    "    |\n"
    "    v  LoginWindow.tenter_connexion()\n"
    "    |\n"
    "    +-- crud.get_utilisateur_by_email(email)\n"
    "    |       SELECT * FROM utilisateur WHERE email = ?\n"
    "    |\n"
    "    +-- security.verifier_mot_de_passe(input, stored_hash)\n"
    "    |       bcrypt.checkpw(bytes, hash_bytes) -> True / False\n"
    "    |\n"
    "    +-- on failure: increment tentatives counter (max 3, then disable button)\n"
    "    |\n"
    "    +-- on success: MainWindow(dict(user)) shown, LoginWindow hidden\n"
    "                    sidebar menu rendered based on user['role']"
)

pdf.h2("4.2  Report Submission Flow  (most complex path)")
pdf.code(
    "Admin fills DepotWindow form -> clicks 'Deposer'\n"
    "    |\n"
    "    v  pdf_handler.deposer_rapport(chemin_source, titre, auteurs, ...)\n"
    "    |\n"
    "    +-- 1. copier_pdf()\n"
    "    |       Sanitize title -> 'ANNEE_TITRE.pdf'\n"
    "    |       Detect filename collision -> append counter suffix\n"
    "    |       shutil.copy2() to storage/rapports/\n"
    "    |\n"
    "    +-- 2. extraire_texte()\n"
    "    |       fitz.open(pdf) -> iterate pages -> page.get_text()\n"
    "    |       returns None if scanned image (no text layer)\n"
    "    |\n"
    "    +-- 3. analyser_similarite(texte_nouveau)\n"
    "    |       SELECT all rapports WHERE texte_extrait IS NOT NULL\n"
    "    |       TfidfVectorizer().fit_transform([new_text] + [all existing])\n"
    "    |       cosine_similarity(matrix[0:1], matrix[1:]) -> score array\n"
    "    |       returns list sorted by score desc, values in %\n"
    "    |\n"
    "    +-- 4. crud.ajouter_rapport()\n"
    "            INSERT INTO rapport (..., statut='Soumis')\n"
    "            returns rapport_id\n"
    "\n"
    "DepotWindow.afficher_resultats_similarite(resultats)\n"
    "    Color codes: >= 70% = red  |  >= 40% = yellow  |  < 40% = green"
)

pdf.h2("4.3  Evaluation Flow")
pdf.code(
    "Encadrant selects report -> double-click or 'Evaluer'\n"
    "    |\n"
    "    v  EvaluationWindow.ouvrir_evaluation()\n"
    "    |\n"
    "    +-- If statut == 'Soumis': crud.changer_statut(id, 'En cours')  <- auto-transition\n"
    "    |\n"
    "    +-- Opens EvaluationDialog (modal)\n"
    "            |\n"
    "            +-- Accepter: evaluer_rapport(id, encadrant_id, note, comment, 'accepter')\n"
    "            |       Verifies rapport.encadrant_id == encadrant_id  (ownership check)\n"
    "            |       UPDATE rapport SET statut='Archive', note=?, commentaire=?\n"
    "            |\n"
    "            +-- Rejeter: requires non-empty commentaire\n"
    "                    UPDATE rapport SET statut='Rejete', note=?, commentaire=?"
)

pdf.h2("4.4  Search Flow  (RBAC-filtered)")
pdf.code(
    "RechercheWindow.lancer_recherche()\n"
    "    |\n"
    "    +-- If role == 'etudiant':              statut_filtre = 'Archive'\n"
    "    +-- If role == 'encadrant' /\n"
    "         'administrateur':                  statut_filtre = None  (see all)\n"
    "    |\n"
    "    v  crud.rechercher_rapports(mot_cle, promotion, option_id, statut_filtre)\n"
    "            Dynamic SQL:  SELECT * FROM rapport WHERE 1=1\n"
    "                          [AND titre / mots_cles / auteurs LIKE ?]\n"
    "                          [AND promotion = ?]\n"
    "                          [AND statut = ?]"
)

# 5. KEY COMPONENTS
pdf.h1("5. Key Components")

pdf.h2("src/database.py  --  Connection Factory + Schema")
pdf.bullet(
    "get_connection(): opens SQLite with row_factory = sqlite3.Row, making all results "
    "accessible as row['column_name'] dicts instead of positional tuples."
)
pdf.bullet(
    "create_tables(): DDL using CREATE TABLE IF NOT EXISTS. The utilisateur table uses "
    "single-table inheritance: all three roles share one table with nullable "
    "role-specific columns (numero_apogee, filiere, departement, ...) enforced by "
    "a CHECK constraint on the 'role' column."
)
pdf.bullet(
    "The rapport table's statut column has a CHECK constraint enforcing the state machine: "
    "Soumis -> En cours -> Evalue / Rejete / Archive."
)

pdf.h2("src/crud.py  --  Data Access Layer")
pdf.bullet(
    "ajouter_utilisateur(): hashes the password before inserting via hasher_mot_de_passe(). "
    "Catches sqlite3.IntegrityError on duplicate email (UNIQUE constraint)."
)
pdf.bullet(
    "evaluer_rapport(): performs an ownership check -- fetches encadrant_id from DB and "
    "compares it to the calling encadrant's ID, preventing cross-encadrant evaluation."
)
pdf.bullet(
    "rechercher_rapports(): builds dynamic SQL with WHERE 1=1 + conditional AND clauses, "
    "safe from SQL injection via parameterized ? placeholders."
)
pdf.bullet(
    "get_statistiques(): fires 6 separate COUNT(*) queries, one per status, for the dashboard."
)

pdf.h2("src/security.py  --  Password Security")
pdf.bullet(
    "hasher_mot_de_passe(): calls bcrypt.gensalt() each time, producing a different hash "
    "for the same password on every call (salt is embedded in the output string)."
)
pdf.bullet(
    "verifier_mot_de_passe(): uses bcrypt.checkpw() which extracts the salt from the stored "
    "hash internally -- no need to store the salt separately."
)

pdf.h2("src/pdf_handler.py  --  PDF + Plagiarism Engine")
pdf.bullet(
    "extraire_texte(): uses PyMuPDF's page.get_text() across all pages. "
    "Returns None for scanned PDFs (image-only, no text layer)."
)
pdf.bullet(
    "analyser_similarite(): builds a TF-IDF matrix where row 0 is the new document and "
    "rows 1..N are all existing stored texts. Computes cosine similarity of row 0 against "
    "all others. Result is a 0-1 float converted to a percentage. Score >= 70% = flagged red."
)
pdf.bullet(
    "deposer_rapport(): the orchestrator -- chains copy -> extract -> similarity -> DB insert, "
    "returning (rapport_id, similarity_results) to the GUI."
)

pdf.h2("gui/main_window.py  --  Application Shell")
pdf.bullet(
    "Uses a QStackedWidget (zone_contenu) as the content area. Each nav click calls "
    "changer_page(), which destroys the old widget with deleteLater() and inserts a "
    "freshly constructed new one -- no page caching."
)
pdf.bullet(
    "The sidebar is built dynamically in creer_sidebar() with 'if role ==' guards, "
    "ensuring menu items only appear for authorized roles."
)
pdf.bullet(
    "The utilisateur dict (explicitly converted via dict(utilisateur) in LoginWindow) "
    "is passed through to all sub-windows as plain data."
)

pdf.h2("gui/preview_window.py  --  PDF Viewer")
pdf.bullet(
    "Extends QDialog (modal). For each page renders via "
    "page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)) -- a zoom matrix scales the pixels."
)
pdf.bullet(
    "Pixmap bytes converted to QImage using raw pix.samples (RGB888 format), "
    "wrapped in QPixmap and set on a QLabel inside a QScrollArea."
)
pdf.bullet(
    "QSpinBox signals are blocked during programmatic navigation (blockSignals(True/False)) "
    "to prevent recursive valueChanged triggers."
)
pdf.bullet(
    "closeEvent() explicitly calls self.doc.close() to release the file handle."
)

pdf.h2("gui/evaluation_window.py  --  Evaluation Workflow")
pdf.bullet(
    "selection_changee(): re-fetches the full report row from DB on every table selection "
    "to ensure data freshness. Enables 'Evaluer' only if statut in ('Soumis', 'En cours')."
)
pdf.bullet(
    "Auto-transition Soumis -> En cours happens silently when an encadrant opens the dialog, "
    "signaling to others that the report is being reviewed."
)
pdf.bullet(
    "EvaluationDialog enforces that a rejection always requires a non-empty comment "
    "before the CRUD call is made."
)

# 6. REPORT STATUS STATE MACHINE
pdf.h1("6. Report Status State Machine")
pdf.code(
    "[Submitted by admin]\n"
    "        |\n"
    "        v\n"
    "     Soumis\n"
    "        | (encadrant opens evaluation dialog)\n"
    "        v\n"
    "    En cours\n"
    "        |\n"
    "   +----+----+\n"
    "   |         |\n"
    "Archive    Rejete\n"
    "(accepted) (rejected -- comment required)"
)
pdf.body(
    "Students (role = etudiant) can only read reports in the Archive state. "
    "Encadrants see only their own assigned reports in the evaluation screen. "
    "Administrators see everything across all states."
)

# 7. NOTABLE DESIGN DECISIONS
pdf.h1("7. Notable Design Decisions")
pdf.table(
    ["Decision", "Consequence"],
    [
        ["No ORM -- raw sqlite3 throughout",
         "Simple for this scale; all connection mgmt is manual (open/close per call)."],
        ["Single-table inheritance for users",
         "Avoids joins for the RBAC model, at the cost of many nullable columns."],
        ["Lazy GUI imports (inside methods)",
         "Avoids circular imports and speeds up initial window load."],
        ["RBAC at two levels (UI sidebar + query filter + ownership check)",
         "Even if menu is bypassed, the DB layer still enforces access rules."],
        ["No session token",
         "Authenticated user passed as a plain dict through the object graph."],
        ["QStackedWidget clears on every nav click",
         "No stale state between views; each visit re-queries the DB fresh."],
    ],
    col_widths=[72, 98]
)

out_path = "c:/Users/AJAR132/Documents/archive_pfa/Project_Technical_Breakdown.pdf"
pdf.output(out_path)
print(f"PDF generated: {out_path}")
