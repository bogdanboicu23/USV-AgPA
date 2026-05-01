#!/usr/bin/env python3
"""Generate PDF report from raport.md with embedded graphs."""

from fpdf import FPDF
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(128)
            self.cell(0, 10, "Quick Sort: Secvential vs MPI", align="C")
            self.ln(12)
            self.set_text_color(0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_draw_color(0, 51, 102)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)
        self.set_text_color(0)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, title)
        self.ln(8)
        self.set_text_color(0)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 11)
        indent = self.l_margin + 6
        self.cell(6, 6, "-")
        self.multi_cell(0, 6, text)
        self.ln(1)

    def code_block(self, text):
        self.set_font("Courier", "", 10)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 5.5, text, fill=True)
        self.ln(3)
        self.set_font("Helvetica", "", 11)

    def bold_text(self, label, text):
        self.set_font("Helvetica", "B", 11)
        self.write(6, label)
        self.set_font("Helvetica", "", 11)
        self.write(6, text)
        self.ln(7)


def build_pdf():
    pdf = Report()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- Title Page ---
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Sortarea Rapida (Quick Sort)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "Implementare Secventiala vs MPI", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_draw_color(0, 51, 102)
    pdf.line(50, pdf.get_y(), pdf.w - 50, pdf.get_y())
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(0)
    pdf.cell(0, 8, "Universitatea Stefan cel Mare Suceava", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Disciplina: Algoritmi Paraleli", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(100)
    pdf.cell(0, 8, "Chisinau, 2025", align="C", new_x="LMARGIN", new_y="NEXT")

    # --- 1. Introducere ---
    pdf.add_page()
    pdf.chapter_title("1. Introducere")
    pdf.body_text(
        "Prezentul raport descrie implementarea si analiza comparativa a algoritmului "
        "de sortare rapida (Quick Sort) in doua variante:"
    )
    pdf.bullet("Secventiala - executie pe un singur procesor")
    pdf.bullet("Paralela - utilizand MPI (Message Passing Interface) cu distribuirea datelor pe mai multe procese")
    pdf.ln(3)
    pdf.body_text(
        "Scopul lucrarii este de a evalua performanta paralelizarii algoritmului Quick Sort "
        "si de a analiza accelerarea (speedup-ul) obtinut prin utilizarea mai multor procese."
    )

    # --- 2. Descrierea algoritmului ---
    pdf.chapter_title("2. Descrierea algoritmului Quick Sort")
    pdf.body_text(
        "Quick Sort este un algoritm de sortare bazat pe principiul divide et impera:"
    )
    pdf.bullet("Se alege un element pivot din tablou")
    pdf.bullet(
        "Se partitioneaza tabloul astfel incat elementele mai mici decat pivotul "
        "se afla in stanga, iar cele mai mari - in dreapta"
    )
    pdf.bullet("Se aplica recursiv algoritmul pe cele doua sub-tablouri")
    pdf.ln(3)
    pdf.bold_text("Complexitatea: ", "")
    pdf.bullet("Cazul mediu: O(n log n)")
    pdf.bullet("Cazul cel mai nefavorabil: O(n^2) - apare rar cu pivotul ales corespunzator")
    pdf.ln(3)
    pdf.section_title("Schema de partitionare Lomuto")
    pdf.body_text(
        "In implementarea data se utilizeaza schema Lomuto, in care pivotul este ultimul "
        "element al sub-tabloului. Indicele i marcheaza granita dintre elementele mai mici "
        "si cele mai mari decat pivotul."
    )

    # --- 3. Implementare secventiala ---
    pdf.chapter_title("3. Implementare secventiala")
    pdf.body_text("Fisierul quicksort_seq.c contine implementarea standard recursiva:")
    pdf.bullet("Se genereaza un tablou aleatoriu de dimensiune N (samanta fixa srand(42) pentru reproductibilitate)")
    pdf.bullet("Se aplica Quick Sort pe intreg tabloul")
    pdf.bullet("Se masoara timpul de executie cu clock_gettime(CLOCK_MONOTONIC)")
    pdf.bullet("Se verifica corectitudinea (tabloul este sortat crescator)")
    pdf.ln(3)
    pdf.bold_text("Compilare: ", "gcc -O2 -Wall -o quicksort_seq quicksort_seq.c")
    pdf.bold_text("Rulare: ", "./quicksort_seq 1000000")

    # --- 4. Implementare MPI ---
    pdf.chapter_title("4. Implementare paralela cu MPI")
    pdf.body_text(
        "Fisierul quicksort_mpi.c implementeaza paralelizarea prin strategia scatter-sort-merge."
    )
    pdf.ln(2)
    pdf.section_title("4.1 Etapele algoritmului paralel")
    pdf.bullet("Generarea datelor - procesul master (rank 0) genereaza tabloul aleatoriu")
    pdf.bullet("Distribuirea - MPI_Scatter imparte tabloul in parti egale intre procese")
    pdf.bullet("Sortarea locala - fiecare proces aplica Quick Sort pe portiunea sa")
    pdf.bullet(
        "Reunirea - se utilizeaza o interclasare arborescenta (tree-based merge): "
        "la fiecare pas, procesele cu rang par primesc date de la procesul vecin cu rang impar, "
        "se interclaseaza cele doua tablouri sortate, procesul se repeta pana cand toate datele "
        "sunt reunite la procesul master"
    )
    pdf.ln(3)
    pdf.section_title("4.2 Schema de comunicare")
    pdf.code_block("Pas 1: P0 <- P1,  P2 <- P3\nPas 2: P0 <- P2")
    pdf.body_text(
        "Aceasta abordare reduce numarul de pasi de comunicare la O(log p), "
        "unde p este numarul de procese."
    )
    pdf.ln(2)
    pdf.bold_text("Compilare: ", "mpicc -O2 -Wall -o quicksort_mpi quicksort_mpi.c")
    pdf.bold_text("Rulare: ", "mpirun -np 4 ./quicksort_mpi 1000000")

    # --- 5. Rezultate experimentale ---
    pdf.add_page()
    pdf.chapter_title("5. Rezultate experimentale")
    pdf.body_text(
        "Testele au fost efectuate pentru dimensiuni ale tabloului: 100K, 500K, 1M, 5M, "
        "10M elemente, cu 1, 2 si 4 procese MPI."
    )
    pdf.ln(3)

    pdf.section_title("5.1 Timpul de executie")
    if os.path.exists("graph_time.png"):
        img_w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image("graph_time.png", x=pdf.l_margin, w=img_w)
        pdf.ln(5)

    pdf.section_title("5.2 Accelerarea (Speedup)")
    if os.path.exists("graph_speedup.png"):
        img_w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image("graph_speedup.png", x=pdf.l_margin, w=img_w)
        pdf.ln(5)

    pdf.body_text("Speedup-ul se calculeaza ca:  S(p) = T_secvential / T_paralel(p)")

    # --- 6. Analiza rezultatelor ---
    pdf.add_page()
    pdf.chapter_title("6. Analiza rezultatelor")
    pdf.section_title("6.1 Observatii")
    pdf.bullet("Pentru tablouri mici (100K), overhead-ul comunicarii MPI depaseste beneficiul paralelizarii")
    pdf.bullet("Pentru tablouri mari (5M, 10M), paralelizarea ofera o accelerare semnificativa")
    pdf.bullet(
        "Speedup-ul nu este liniar din cauza: overhead-ului de comunicare "
        "(MPI_Scatter, MPI_Send/MPI_Recv), fazei de interclasare secventiale la reunirea "
        "datelor, si dezechilibrului potential al datelor intre procese"
    )
    pdf.ln(3)
    pdf.section_title("6.2 Legea lui Amdahl")
    pdf.body_text(
        "Conform legii lui Amdahl, speedup-ul maxim este limitat de fractiunea secventiala "
        "a algoritmului. Faza de interclasare finala si distribuirea datelor reprezinta "
        "componente secventiale care limiteaza scalabilitatea."
    )

    # --- 7. Concluzii ---
    pdf.chapter_title("7. Concluzii")
    pdf.bullet("Algoritmul Quick Sort se preteaza bine la paralelizare prin strategia scatter-sort-merge")
    pdf.bullet("MPI permite distribuirea eficienta a datelor si reunirea rezultatelor")
    pdf.bullet("Beneficiul paralelizarii creste odata cu dimensiunea datelor de intrare")
    pdf.bullet(
        "Pentru aplicatii practice, este important sa se aleaga numarul optim de procese "
        "in functie de dimensiunea problemei si de overhead-ul de comunicare"
    )

    # --- 8. Bibliografie ---
    pdf.ln(5)
    pdf.chapter_title("8. Bibliografie")
    pdf.bullet("Cormen, T.H., Leiserson, C.E., Rivest, R.L., Stein, C. - Introduction to Algorithms, MIT Press")
    pdf.bullet("Pacheco, P. - An Introduction to Parallel Programming, Morgan Kaufmann")
    pdf.bullet("MPI Forum - MPI: A Message-Passing Interface Standard, https://www.mpi-forum.org/")

    pdf.output("raport.pdf")
    print("Generated raport.pdf")


if __name__ == "__main__":
    build_pdf()
