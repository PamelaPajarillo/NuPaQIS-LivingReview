from utils import *

# Input Files
YAML_FILE = 'NUPAQIS.yaml'
CATEGORIES_YAML = 'NUPAQIS_CATEGORIES.yaml'

# Get categories from CSV file
df_csv_nupa, categories_nupa, df_csv_qis, categories_qis = get_categories(CATEGORIES_YAML)

# Get dataframe of BibTeX and CSV
df = get_dataframe(YAML_FILE, categories_nupa, categories_qis)

# ***** ---------------------------------------------------------------------------------------
# ***** MARKDOWN FILES ------------------------------------------------------------------------
# ***** ---------------------------------------------------------------------------------------
# Output Markdown Files
OUTPUT_FILE_MAIN = open("README.md","w")
OUTPUT_FILE_NUPA = open("BY_NUPA/README.md","w")
OUTPUT_FILE_QIS = open("BY_QIS/README.md","w")

# ***** MAIN MD -----------------------------------------------------------------------
OUTPUT_FILE_MAIN.write("#  **A Living Review of Quantum Information Science in Nuclear and Particle Physics**\n\n")

OUTPUT_FILE_MAIN.write("[![DOWNLOAD_PDF](https://img.shields.io/badge/Download-PDF_Version-81b7df)](https://docs.google.com/viewer?url=https://raw.githubusercontent.com/PamelaPajarillo/NUPAQIS-LivingReview/main/NUPAQIS.pdf) \n\n\n")
OUTPUT_FILE_MAIN.write("Authors: Pamela Pajarillo, So Chigusa, Sokratis Trifinopoulos, Jesse Thaler \n \n")
OUTPUT_FILE_MAIN.write("*Inspired by <a href=\"https://iml-wg.github.io/HEPML-LivingReview/\">\"A Living Review of Machine Learning for High Energy Physics\"</a>, the goal of this repository is to provide an extensive list of citations for those developing and applying quantum information approaches to experimental, phenomenological, or theoretical analyses.  Applications of quantum information science to high energy physics is a relatively new field of research.  This repository will be updated as often as possible with the relevant literature.  Suggestions are most welcome.*\n\n")
OUTPUT_FILE_MAIN.write("The goal of this repository is to collect references for quantum information science as applied to particle and nuclear physics. The papers are listed in reverse chronological order. \n\n")

OUTPUT_FILE_MAIN.write("The repository is organized in two ways: \n* [![MAIN_TO_NUPA](https://img.shields.io/badge/Link_to-Living_Review_by_Nuclear_and_Particle_Physics-5BC0EB)](/BY_NUPA#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-nupa-topics) \n* [![MAIN_TO_NUPA](https://img.shields.io/badge/Link_to-Living_Review_by_Quantum_Information_Science-9BC53D)](/BY_QIS#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-qis-topics)\n\n")
OUTPUT_FILE_MAIN.write("These are then organized by subtopics listed below. \n\n")

# ***** LIST CATEGORIES -----------------------------------------------------------------------
OUTPUT_FILE_MAIN.write("##  **Nuclear and Particle Physics (NuPa) Topics**\n\n")
list_subcategories_to_md(OUTPUT_FILE_MAIN, categories_nupa, df_csv_nupa, "NUPA")
OUTPUT_FILE_MAIN.write("##  **Quantum Information Science (QIS) Topics**\n\n")
list_subcategories_to_md(OUTPUT_FILE_MAIN, categories_qis, df_csv_qis, "QIS")

OUTPUT_FILE_MAIN.close()

# ***** BY NUPA MD -----------------------------------------------------------------------
OUTPUT_FILE_NUPA.write("#  **A Living Review of Quantum Information Science in Nuclear and Particle Physics Organized by Nuclear and Particle Physics Topics**\n\n")
OUTPUT_FILE_NUPA.write("[![BY_QIS](https://img.shields.io/badge/Link_to-Living_Review_by_Quantum_Information_Science-9BC53D)](/BY_QIS#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-qis-topics) \t\n")
OUTPUT_FILE_NUPA.write("[![NUPA_TO_MAIN](https://img.shields.io/badge/Link_to-Living_Review_Home_-FDE74C)](/../../#readme) \n\n")
write_papers_to_md(df, OUTPUT_FILE_NUPA, categories_nupa, categories_qis, "NUPA", "QIS")
OUTPUT_FILE_NUPA.close()

# ***** BY QIS MD -----------------------------------------------------------------------
OUTPUT_FILE_QIS.write("#  **A Living Review of Quantum Information Science in Nuclear and Particle Physics Organized by Quantum Information Science Topics**\n\n")
OUTPUT_FILE_QIS.write("[![QIS_TO_NUPA](https://img.shields.io/badge/Link_to-Living_Review_by_Nuclear_and_Particle_Physics-5BC0EB)](/BY_NUPA#a-living-review-of-quantum-information-science-in-nuclear-and-particle-physics-organized-by-nupa-topics) \t\n")
OUTPUT_FILE_QIS.write("[![QIS_TO_MAIN](https://img.shields.io/badge/Link_to-Living_Review_Home_-FDE74C)](/../../#readme) \n\n")
write_papers_to_md(df, OUTPUT_FILE_QIS, categories_qis, categories_nupa, "QIS", "NUPA")
OUTPUT_FILE_QIS.close()

# ***** ------------------------------------------------------------------------------------
# ***** LATEX FILES ------------------------------------------------------------------------
# ***** ------------------------------------------------------------------------------------
# Output LaTeX Files
OUTPUT_FILE = open("INTRODUCTION.tex","w")
OUTPUT_FILE.write('\section{Introduction}\n\n')
OUTPUT_FILE.write('The purpose of this note is to collect references for quantum information science as applied to particle and nuclear physics.  The papers are listed in reverse chronological order.  In order to be as useful as possible, this document will continually change. Please check back \\footnote[2]{See \href{https://github.com/PamelaPajarillo/NUPAQIS-LivingReview}{https://github.com/PamelaPajarillo/NUPAQIS-LivingReview}.} regularly.  You can simply download the .bib file to get all of the latest references.  Suggestions are most welcome.')
OUTPUT_FILE_NUPA = open("BYNUPA.tex","w")
OUTPUT_FILE_QIS = open("BYQIS.tex","w")
OUTPUT_FILE_BIB = open("NUPAQIS.bib","w")

# ***** MAIN LATEX FILES -----------------------------------------------------------------------
write_papers_to_tex(df, OUTPUT_FILE_NUPA, categories_nupa, categories_qis, "NUPA", "QIS")
write_papers_to_tex(df, OUTPUT_FILE_QIS, categories_qis, categories_nupa, "QIS", "NUPA")
write_bib(df, OUTPUT_FILE_BIB)
OUTPUT_FILE.close()
OUTPUT_FILE_NUPA.close()
OUTPUT_FILE_QIS.close()
OUTPUT_FILE_BIB.close()