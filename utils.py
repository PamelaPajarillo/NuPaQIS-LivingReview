import sys
import re
import pandas as pd
from datetime import date
import urllib3
import json
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import seaborn as sns

def format_pub_info(run, date_arxiv, date_doi, eprint, eprint_url, doi, doi_url):
    date_vec_arxiv = date_arxiv.split("-")
    date_vec_doi = date_doi.split("-")

    str_arxiv = ''
    str_doi = ''

    if date_arxiv != 'nan':
        # Prefix 
        if run == 'md':
            str_arxiv = "\n+ <strong>Posted on <a href=\"%s\">arXiv:%s</a>:</strong> " % (eprint_url, eprint)
        elif run == 'tex':
            str_arxiv = "\item \\textbf{Posted on arXiv:} "
        # Append Date
        if len(date_vec_arxiv) == 3:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), int(date_vec_arxiv[2])).strftime("%d %B %Y")
        elif len(date_vec_arxiv) == 2:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), 1).strftime("%B %Y")
        else:
            str_arxiv += date(int(date_vec_arxiv[0]), 1, 1).strftime("%Y")
    
    if date_doi != 'nan':
        # Prefix
        if run == 'md':
            str_doi = "\n+ <strong>Published in <a href=\"%s\">%s</a>:</strong> " % (doi_url, doi)
        elif run == 'tex':
            str_doi = "\item \\textbf{Published in %s:} " % (doi)
        # Append Date
        if len(date_vec_doi) == 3:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), int(date_vec_doi[2])).strftime("%d %B %Y")
        elif len(date_vec_doi) == 2:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), 1).strftime("%B %Y")
        else:
            str_doi += date(int(date_vec_doi[0]), 1, 1).strftime("%Y")
            
    if str_arxiv != '' and str_doi != '':
        return str_arxiv + ' ' +  str_doi
    elif str_arxiv != '' and str_doi == '':
        return str_arxiv
    elif str_arxiv == '' and str_doi != '':
        return str_doi
    else:
        return ''

def get_year(date_arxiv, date_doi):
    date_vec_arxiv = date_arxiv.split("-")
    date_vec_doi = date_doi.split("-")

    str_arxiv = ''
    str_doi = ''

    if date_arxiv != 'nan':
       # Append Date
        if len(date_vec_arxiv) == 3:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), int(date_vec_arxiv[2])).strftime("%Y")
        elif len(date_vec_arxiv) == 2:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), 1).strftime("%Y")
        else:
            str_arxiv += date(int(date_vec_arxiv[0]), 1, 1).strftime("%Y")

    if date_doi != 'nan':
        # Append Date
        if len(date_vec_doi) == 3:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), int(date_vec_doi[2])).strftime("%Y")
        elif len(date_vec_doi) == 2:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), 1).strftime("%Y")
        else:
            str_doi += date(int(date_vec_doi[0]), 1, 1).strftime("%Y")
            
    if str_arxiv != '':
        return str_arxiv
    elif str_doi != '':
        return str_doi
    else:
        return ''
    
def get_dataframe(yaml_file, categories_hep, categories_qis):
    
    # Load the YAML file
    with open(yaml_file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    # Convert the YAML data to a Pandas DataFrame
    df = pd.DataFrame.from_dict(data)

    # Check to make sure each paper's categories are valid
    def check_categories(categories, category_list):
        for category in categories.split(', ')[1::2]:
            if category not in category_list:
                return False
        return True
    
    # Check to make sure each paper has at least one valid NUPA category and at least one valid QIS category
    exit_condition = False
    df["NUPA_Check"] = df["NUPA_Categories"].str.contains('|'.join(categories_hep), case=False)
    df["QIS_Check"] = df["QIS_Categories"].str.contains('|'.join(categories_qis), case=False)
    df["NUPA_Category_Check"] = df["NUPA_Categories"].apply(lambda x: check_categories(x, categories_hep))
    df["QIS_Category_Check"] = df["QIS_Categories"].apply(lambda x: check_categories(x, categories_qis))
    check_hep = df[~df["NUPA_Check"] | ~df["NUPA_Category_Check"]]
    check_qis = df[~df["QIS_Check"]| ~df["QIS_Category_Check"]]
    if len(check_hep) > 0:
        print("The following papers have invalid NUPA categories:")
        print(check_hep[['ID']])
        exit_condition = True
    if len(check_qis) > 0:
        print("The following papers have invalid QIS categories:")
        print(check_qis[['ID']])
        exit_condition = True

    # Stop if there are any invalid categories
    if exit_condition:
        sys.exit(1)
    
    # Parse out primary category and secondary categories
    def sort_categories(categories, primary = False):
        if primary:
            return categories.split(', ', 1)[0]
        else:
            return categories.split(', ', 1)[1] if len(categories.split(', ')) > 1 else 'N/A'
    
    df["NUPA_Primary"] = df["NUPA_Categories"].apply(lambda x: sort_categories(x, primary = True))
    df["NUPA_Secondary"] = df["NUPA_Categories"].apply(lambda x: sort_categories(x, primary = False))
    df["QIS_Primary"] = df["QIS_Categories"].apply(lambda x: sort_categories(x, primary = True))
    df["QIS_Secondary"] = df["QIS_Categories"].apply(lambda x: sort_categories(x, primary = False))

    def get_inspirehep_metadata(label, http):
        url = 'https://inspirehep.net/api/literature/' + str(label)
        http_request = http.request('GET', url)
        metadata = json.loads(http_request.data)
        return metadata

    def get_doi_metadata(label, http):
        if label != 'nan':
            url = 'https://inspirehep.net/api/doi/' + str(label)
            http_request = http.request('GET', url)
            metadata = json.loads(http_request.data)
            return metadata['metadata']
        else:
            return json.loads('{}')

    def get_author_list(metadata):
        author_list = ''
        if 'authors' in metadata['metadata'].keys():
            for i in metadata['metadata']['authors']:
                author_list += i['full_name'] + " and "
            author_list = author_list[:-5]
        else:
            author_list =  'nan'
        
        # Fix Formatting
        author_list = author_list.split(' and ')
        formatted_author_list = []
        for author in author_list:
            if ',' in author:
                formatted_author_list.append(author.split(',')[1].strip() + ' ' + author.split(',')[0].strip())
        fixed_author = ', '.join(formatted_author_list)
        return fixed_author

    def get_author_url_list(metadata):
        author_list = ''
        for i in metadata['metadata']['authors']:
            author_name = i['full_name']
            if ',' in author_name:
                author_name = author_name.split(',')[1].strip() + ' ' + author_name.split(',')[0].strip()
            author_list += "<a href=\"%s\"> %s</a>" % (i['record']['$ref'].replace('/api',''), author_name) + ", "
        return author_list[:-2]
    
    def get_journal_doi(doi, metadata_doi):
        if doi != 'nan':
            if len(metadata_doi['publication_info']) != 1:
                full_journal_name = ''
                for i in metadata_doi['publication_info']:
                    if 'pubinfo_freetext' in i.keys():
                        full_journal_name = i['pubinfo_freetext']
                    elif 'journal_title' in i.keys():
                        full_journal_name = i['journal_title']
                return full_journal_name
            elif 'pubinfo_freetext' in metadata_doi['publication_info'][0].keys():
                return metadata_doi['publication_info'][0]['pubinfo_freetext']
            elif 'journal_title' in metadata_doi['publication_info'][0].keys():
                return metadata_doi['publication_info'][0]['journal_title']
            else:
                return 'nan'
        else:
            return 'nan'
    
    def get_bibtex(metadata, http):
        url = metadata["links"]["bibtex"]
        bibtex_request = http.request('GET', url)
        return bibtex_request.data.decode('utf-8')
            
    # Read InspireHEP entry
    http = urllib3.PoolManager()
    df['ID'] = df['ID'].astype(str)
    df["metadata"] = df.apply(lambda x: get_inspirehep_metadata(x["ID"], http), axis=1)
    df["inspirehep_url"] = "https://inspirehep.net/literature/" + df["ID"]
    df["title"] = df["metadata"].apply(lambda x: x['metadata']['titles'][0]['title'])
    df["authors"] = df["metadata"].apply(lambda x: get_author_list(x))
    df["authors_url"] = df["metadata"].apply(lambda x: get_author_url_list(x))
    df["eprint"] = df["metadata"].apply(lambda x: x['metadata']['arxiv_eprints'][0]['value'] if 'arxiv_eprints' in x['metadata'].keys() else 'nan')
    df["doi"] = df["metadata"].apply(lambda x: x['metadata']['dois'][0]['value'] if 'dois' in x['metadata'].keys() else 'nan')
    df["eprint_url"] = df["eprint"].apply(lambda x: "https://arxiv.org/abs/" + x if x != 'nan' else 'nan')
    df["doi_url"] = df["doi"].apply(lambda x: "https://doi.org/" + x if x != 'nan' else 'nan')
    df["arxiv_date"] = df["metadata"].apply(lambda x: x['metadata']['preprint_date'] if 'preprint_date' in x['metadata'].keys() else 'nan')
    df["doi_date"] = df["metadata"].apply(lambda x: x['metadata']['imprints'][0]['date'] if 'imprints' in x['metadata'].keys() else (x['metadata']['publication_info'][0]['year'] if 'publication_info' in x['metadata'].keys() and 'journal_title' in x['metadata']['publication_info'][0] else 'nan'))
    df["metadata_doi"] = df.apply(lambda x: get_doi_metadata(x['doi'], http), axis=1)
    df["journal_name"] = df.apply(lambda x: get_journal_doi(x['doi'], x['metadata_doi']), axis=1)
    df["Publish_Info_md"] = df.apply(lambda x: format_pub_info('md', str(x['arxiv_date']), str(x['doi_date']), str(x['eprint']), str(x['eprint_url']), str(x['journal_name']), str(x['doi_url'])), axis=1)
    df["Publish_Info_latex"] = df.apply(lambda x: format_pub_info('tex', str(x['arxiv_date']), str(x['doi_date']), str(x['eprint']), str(x['eprint_url']), str(x['journal_name']), str(x['doi_url'])), axis=1)
    df["bibtex_tag"] = df["metadata"].apply(lambda x: x['metadata']['texkeys'][0])
    df["bibtex"] = df["metadata"].apply(lambda x: get_bibtex(x, http))
    df["year"] = df.apply(lambda x: get_year(str(x['arxiv_date']), str(x['doi_date'])), axis=1)
    # Compress dataframe with useful information
    df = df[["ID", "title", "authors", "authors_url", "eprint", "doi", "eprint_url", "doi_url", "inspirehep_url", "Publish_Info_md", "Publish_Info_latex",
             "NUPA_Primary", "NUPA_Secondary", "QIS_Primary", "QIS_Secondary", "bibtex_tag", "bibtex", "year"]]
    return df

def get_categories(yaml_file):
    # Read YAML file
    df_categories = {}
    list_categories = {}
    categories_description = {}
    with open(yaml_file, 'r') as file:
        data = yaml.load_all(file, Loader=yaml.FullLoader)

        # Convert the YAML data to a Pandas DataFrame
        for idx, d in enumerate(data):
            df_categories[idx] = pd.DataFrame.from_dict(d)
            list_categories[idx] = df_categories[idx]['Category'].tolist()
            categories_description[idx] = df_categories[idx]['Description'].tolist()
    
    return list_categories[0], categories_description[0], list_categories[1], categories_description[1]

def plot_histogram(df, run):
    counts = df['%s_Primary' % run].value_counts()
    title = "Nuclear and Particle Physics" if run == 'NUPA' else "Quantum Information Science"
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 8))
    bar_color = "skyblue" if run == 'NUPA' else "lightgreen"
    # Plot
    bars = plt.bar(counts.index, counts.values, color=bar_color)
    plt.xlabel("%s Categories" % title, fontsize=12)
    plt.ylabel("Number of Papers", fontsize=12)
    plt.title("Number of Papers per %s Category" % title, fontsize=16, pad=20)
    plt.xticks(rotation=75, ha='right', fontsize=10)

    # Add value labels above each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2,
                 height + 0.3,
                 str(int(height)),
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{run}_Histogram.png", dpi=300)


# def plot_2D_nupaqis_heatmap(df, categories_nupa, categories_qis):
#     heatmap_data = np.zeros((len(categories_nupa), len(categories_qis)))

#     for i, nupa_cat in enumerate(categories_nupa):
#         for j, qis_cat in enumerate(categories_qis):
#             count = len(df[(df['NUPA_Primary'] == nupa_cat) & (df['QIS_Primary'] == qis_cat)])
#             heatmap_data[i, j] = count

#     # Plot heatmap
#     plt.figure(figsize=(15, 15))
#     plt.imshow(heatmap_data, cmap='GnBu', aspect='auto')
#     plt.colorbar(label='Number of Papers')
#     plt.xticks(ticks=np.arange(len(categories_qis)), labels=categories_qis, rotation=90)
#     plt.yticks(ticks=np.arange(len(categories_nupa)), labels=categories_nupa)
#     plt.xlabel('Quantum Information Science (QIS) Topics')
#     plt.ylabel('Nuclear and Particle Physics (NuPa) Topics')
#     plt.title('2D Heatmap of NuPa vs QIS Topics in NUPAQIS Living Review')
#     plt.tight_layout()
#     plt.savefig('NUPAQIS_2D_Heatmap.png', dpi=300)
#     plt.close()

def plot_2D_nupaqis_heatmap(df, categories_nupa, categories_qis):

    # Build the matrix
    heatmap_data = np.zeros((len(categories_nupa), len(categories_qis)))

    for i, nupa_cat in enumerate(categories_nupa):
        for j, qis_cat in enumerate(categories_qis):
            count = len(df[(df['NUPA_Primary'] == nupa_cat) & 
                           (df['QIS_Primary'] == qis_cat)])
            heatmap_data[i, j] = count

    # --- Custom colormap that shows white for zero ---
    cmap = plt.cm.Blues
    cmap = cmap.copy()
    cmap.set_under(color='white')

    max_count = np.max(heatmap_data)
    norm = colors.Normalize(vmin=0.001, vmax=max_count)

    # Plot heatmap
    plt.figure(figsize=(16, 14))
    plt.imshow(heatmap_data, cmap=cmap, norm=norm, aspect='auto')

    # Colorbar
    cbar = plt.colorbar(label='Number of Papers')
    cbar.ax.tick_params(labelsize=12)

    # Axis labels
    plt.xticks(
        ticks=np.arange(len(categories_qis)),
        labels=categories_qis,
        rotation=90,
        fontsize=10
    )
    plt.yticks(
        ticks=np.arange(len(categories_nupa)),
        labels=categories_nupa,
        fontsize=10
    )
    plt.xlabel('Quantum Information Science (QIS) Topics', fontsize=12)
    plt.ylabel('Nuclear and Particle Physics (NuPa) Topics', fontsize=12)
    plt.title('2D Heatmap of NuPa vs QIS Topics in NUPAQIS Living Review',
              fontsize=16, pad=20)

    # -------------------------------
    # ⭐ Add numbers inside each cell
    # -------------------------------
    for i in range(len(categories_nupa)):
        for j in range(len(categories_qis)):
            val = heatmap_data[i, j]

            # Choose text color based on background intensity
            if val > max_count * 0.5:
                text_color = "white"
            else:
                text_color = "black"

            plt.text(j, i, int(val),
                     ha='center', va='center',
                     fontsize=9, color=text_color)
    # -------------------------------

    # Optional: grid lines for clarity
    plt.gca().set_xticks(np.arange(-0.5, len(categories_qis), 1), minor=True)
    plt.gca().set_yticks(np.arange(-0.5, len(categories_nupa), 1), minor=True)
    plt.grid(which='minor', color='gray', linestyle='-', linewidth=0.2, alpha=0.4)

    plt.tight_layout()
    plt.savefig('NUPAQIS_2D_Heatmap.png', dpi=300)
    plt.close()

def list_subcategories_to_md(OUTPUT_FILE_MAIN, subcategories, description, run_type):
    textcolor = 'textbfcolor9bc53d' if run_type == 'NUPA' else 'textbfcolor5bc0eb'
    for category in subcategories:
        if (category != 'Reviews') and (category != 'Whitepapers and Proceedings'):
            OUTPUT_FILE_MAIN.write("<details>\n")
            OUTPUT_FILE_MAIN.write("<summary> <b>%s: </b> <a href=\"/BY_%s/README.md#%s%s\"> Link to Papers </a>  <code>Expand for Description</code> </summary>\n\n" % (category, run_type, textcolor, category.replace(" ", "-").lower()))
            OUTPUT_FILE_MAIN.write("\n\n%s" % (description[subcategories.index(category)]))
            OUTPUT_FILE_MAIN.write("</details>")
        elif (category == 'Reviews'):
            OUTPUT_FILE_MAIN.write("<details>\n")
            OUTPUT_FILE_MAIN.write("<summary> <b>Reviews and Whitepapers and Proceedings: </b> <a href=\"/BY_%s/README.md#textbfreviews-and-whitepapers\"> Link to Papers </a>  <code>Expand for Description</code> </summary>\n\n" % (run_type))
            OUTPUT_FILE_MAIN.write("\n\nThe references below contain (static) reviews and whitepapers listed in applications of quantum information science to particle physics. Note that the majority of the references are from the Snowmass Community Planning Exercises." )
            OUTPUT_FILE_MAIN.write("</details>")
        else:
            continue
    OUTPUT_FILE_MAIN.write("\n\n")
    
def write_papers_to_md(df, output_file, categories_main, categories_sub, main_type, sub_type):

    # Get Main Categories
    for main_category in categories_main:

        # Print Title of Main Category
        if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
            if main_type != "NUPA":
                output_file.write("##  $\\textbf{{\color{#5BC0EB}%s}}$ \n\n" % (main_category))
            else:
                output_file.write("##  $\\textbf{{\color{#9BC53D}%s}}$ \n\n" % (main_category))
        elif (main_category == 'Reviews'):
            output_file.write("##  $\\textbf{Reviews and Whitepapers and Proceedings}$ \n\n")

        # Retrieve papers by checking for substring in categories
        df_main = df.loc[df['%s_Primary' % main_type].str.contains(main_category, case=False)]
        
        for sub_category in categories_sub:
            
            # Retrieve papers by checking for substring in categories
            df_sub = df_main.loc[df['%s_Primary' % sub_type].str.contains(sub_category, case=False)]
            papers = df_sub.values.tolist()

            if len(papers) > 0:
                # Print Title of Category
                if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
                    if sub_type != "NUPA":
                        output_file.write("###  $\\textbf{{\color{#5BC0EB}%s}}$ \n\n" % (sub_category))
                    else:
                        output_file.write("###  $\\textbf{{\color{#9BC53D}%s}}$ \n\n" % (sub_category))

                else:
                    output_file.write("###  $\\textbf{%s}$ \n\n" % (sub_category.replace(" ", " \space ")))

                # Formatting and write to file
                for paper in papers:

                    output_file.write("<details>\n")

                    if (str(paper[4]) != 'nan') and (str(paper[5]) != 'nan'):
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code> </summary>" % (paper[17], paper[1], paper[6], paper[7], paper[8]))
                    elif str(paper[4]) != 'nan':
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[6], paper[8]))
                    elif str(paper[5])!= 'nan':
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[7], paper[8]))
                    else:
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[8]))

                    # Write brief description and summary of paper
                    output_file.write("\n\n+ <strong>Authors:</strong> %s%s" % (paper[3], paper[9]))
                    output_file.write("</details>\n\n")
                
        # Crosslists Papers (Add papers from secondary categories)
        df_crosslisted = df.loc[df['%s_Secondary' % main_type].str.contains(main_category, case=False)]
        crosslisted_papers = df_crosslisted.values.tolist()
        if len(crosslisted_papers) > 0:
            if sub_type != "NUPA":
                output_file.write("###  $\\textbf{{\color{#5BC0EB}Crosslists}}$ \n\n")
            else:
                output_file.write("###  $\\textbf{{\color{#9BC53D}Crosslists}}$ \n\n")
            for paper in crosslisted_papers:
                output_file.write("<details>\n")

                if (str(paper[4]) != 'nan') and (str(paper[5]) != 'nan'):
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code> </summary>" % (paper[17], paper[1], paper[6], paper[7], paper[8]))
                elif str(paper[4]) != 'nan':
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[6], paper[8]))
                elif str(paper[5])!= 'nan':
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[7], paper[8]))
                else:
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1],paper[8]))

                # Write brief description and summary of paper
                output_file.write("\n\n+ <strong>Authors:</strong> %s%s" % (paper[3], paper[9]))
                output_file.write("</details>\n\n")

                output_file.write("\n\n")

def write_papers_to_tex(df, file, categories_main, categories_sub, main_type, sub_type):
    # Get Categories and Subcategories
    if main_type == 'NUPA':
        file.write("\section{Nuclear and Particle Physics in Quantum Information Science}\n\n")
    elif main_type == 'QIS':
        file.write("\section{Quantum Information Science in Nuclear and Particle Physics}\n\n")
    
    for main_category in categories_main:
        # Print Title of Main Category
        if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
            file.write("\subsection{%s}\n\n" % main_category)
        elif (main_category == 'Reviews'):
            file.write("\subsection{Reviews and Whitepapers and Proceedings}\n\n")

        # Retrieve papers by checking for substring in categories
        df_main = df.loc[df['%s_Primary' % main_type].str.contains(main_category, case=False)]
        
        for sub_category in categories_sub:
            
            # Retrieve papers by checking for substring in categories
            df_sub = df_main.loc[df['%s_Primary' % sub_type].str.contains(sub_category, case=False)]
            papers = df_sub.values.tolist()

            if len(papers) > 0:
                
                file.write("\subsubsection{%s}\n\n" % sub_category)

                # Formatting and write to file
                for paper in papers:

                    # Fix Author Names with Special Characters
                    paper[2] = re.sub(r"ã", r"\~{a}", paper[2])
                    paper[2] = re.sub(r"á", r"\'{a}", paper[2])
                    paper[2] = re.sub(r"é", r"\`{e}", paper[2])
                    paper[2] = re.sub(r"é", r"\'{e}", paper[2])
                    paper[2] = re.sub(r"í", r"\'{i}", paper[2])
                    paper[2] = re.sub(r"ö", r"\"{o}", paper[2])
                    paper[2] = re.sub(r"ó", r"\'{o}", paper[2])
                    paper[2] = re.sub(r"ñ", r"\~{n}", paper[2])
                    paper[2] = re.sub(r"ü", r"\"{u}", paper[2])
                    paper[2] = re.sub(r"ú", r"\'{u}", paper[2])
                    paper[2] = re.sub(r"ź", r"\'{z}", paper[2])

                    file.write("\paragraph{%s~\cite{%s}}\n" % (paper[1], paper[15]))
                    file.write("\\begin{itemize}\n")
                    file.write("\t\item \\textbf{Authors:} %s\n\t%s\n" % (paper[2], paper[10]))                    
                    file.write("\end{itemize}\n\n")
                file.write("\n\n")
        
        # Crosslists Papers (Add papers from secondary categories)
        df_crosslisted = df.loc[df['%s_Secondary' % main_type].str.contains(main_category, case=False)]
        crosslisted_papers = df_crosslisted.values.tolist()
        if len(crosslisted_papers) > 0:
            file.write("\subsubsection{Crosslists}\n\n")
            # Formatting and write to file
            for paper in crosslisted_papers:

                # Fix Author Names with Special Characters
                paper[2] = re.sub(r"ã", r"\~{a}", paper[2])
                paper[2] = re.sub(r"á", r"\'{a}", paper[2])
                paper[2] = re.sub(r"é", r"\`{e}", paper[2])
                paper[2] = re.sub(r"é", r"\'{e}", paper[2])
                paper[2] = re.sub(r"í", r"\'{i}", paper[2])
                paper[2] = re.sub(r"ö", r"\"{o}", paper[2])
                paper[2] = re.sub(r"ó", r"\'{o}", paper[2])
                paper[2] = re.sub(r"ñ", r"\~{n}", paper[2])
                paper[2] = re.sub(r"ü", r"\"{u}", paper[2])
                paper[2] = re.sub(r"ú", r"\'{u}", paper[2])
                paper[2] = re.sub(r"ź", r"\'{z}", paper[2])

                file.write("\paragraph{%s~\cite{%s}}\n" % (paper[1], paper[15]))
                file.write("\\begin{itemize}\n")
                file.write("\t\item \\textbf{Authors:} %s\n\t%s\n" % (paper[2], paper[10]))                    
                file.write("\end{itemize}\n\n")
            file.write("\n\n")

def write_bib(df, OUTPUT_FILE_BIB):
    for paper in df.values.tolist():
        OUTPUT_FILE_BIB.write("%s\n" % paper[16])