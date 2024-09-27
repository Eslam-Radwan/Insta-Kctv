'''
Place all code relating to processing and loading data here
'''
import os
import json
import argparse
import regex as re
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import logging
logger = logging.getLogger(__name__)


endpoint = os.environ.get("KRLFORMRECOGNIZER_ENDPOINT")
key = os.environ.get("KRLFORMRECOGNIZER_KEY")


def analyze_layout(doc_path):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    doc_analysis_model = "prebuilt-document"
    logger.info(f'Processing doc {doc_path} with {doc_analysis_model}')
    with open(doc_path, 'rb') as fin:
        poller = document_analysis_client.begin_analyze_document(
                doc_analysis_model, fin)
    result = poller.result()
    with open(f'{doc_path}.json', 'w', encoding='utf-8') as fout:
        data = json.dumps(result.to_dict(), indent=4, ensure_ascii=False)
        fout.write(data)
    return f'{doc_path}.json'

def get_data(doc_path, out_dir):
    if not os.path.exists(f'{doc_path}.json'):
        json_path = analyze_layout(doc_path)
    else:
        json_path = f'{doc_path}.json'


    logger.info(f'Loading json: {json_path}')
    doc_json = json.loads(open(json_path, encoding="utf8").read())
    return doc_json

def get_figures(figure_json_path):
    figure_json = json.load(open(figure_json_path))
    figs = {}
    descriptions = []
    for fig in figure_json:
        prompt_text = f'Figure Name: {fig["figType"]} {fig["name"]}\n'\
                    f'Figure Caption: {fig["caption"]}'
        descriptions.append(prompt_text)
        figs[f'{fig["figType"]} {fig["name"]}'] = {
            "promptText": fig_desc,
            "renderURL": fig['renderURL'],
            "caption": fig["caption"],
            # "description": "" # TODO

        }
        
def prepare_latex_for_eval(input_latex):
    # Get title 
    title_text = re.findall(r"\\(author|title|date)\{(.*)\}", input_latex)
    if len(title_text) > 0:
        title_text = '\n'.join((t[1] for t in title_text))
        input_latex = re.sub(r"\\titlepage", repr(title_text), input_latex)
        input_latex = re.sub(r"\\maketitle", repr(title_text), input_latex)
        input_latex = re.sub(r"\\(author|title|date)\{(.*)\}", "", input_latex)
    # Get document text    
    cleaned_input_latex = re.findall(r"\\begin\{document\}([\S\s]*)\\end\{document\}", input_latex)
    if len(cleaned_input_latex) > 0:
        input_latex = cleaned_input_latex[0]


    # Get frames
    frames = []
    curr_frame_text = ''
    for line in input_latex.split('\n'):
        line_command = re.findall(r"\\(\w+)\{(.+)\}", line)
        # If new frame, append curr text if non empty, then reset frame
        if line_command==[('begin', 'frame')] or line_command==[('begin', 'block')]:
            if curr_frame_text != '':
                frames.append(curr_frame_text)
            curr_frame_text = ''
        # If end frame, append curr text then reset frame
        elif line_command==[('end', 'frame')] or line_command==[('end', 'block')]:
            frames.append(curr_frame_text)
            curr_frame_text = ''
        # If text in a command, strip command text and only append text
        elif (line_command != []):
            if line_command[0][0] not in ['begin', 'end']:
                curr_frame_text += line_command[0][-1] + '\n'
        # Else, strip "item" command and append text
        else:
            no_item_text = re.findall(r"(\\item )?(.+)", line)
            if no_item_text:
                curr_frame_text +=  no_item_text[0][-1] + '\n'

    if curr_frame_text != '':
        frames.append(curr_frame_text)

    return frames

def parse_gpt_response(response):
    text = ''
    for key in response:
        if key not in ['Content', 'Document Title', 'Document Authors']:
                text += f'{key}\n'
        if type(response[key]) == dict:
            text += parse_gpt_response(response[key])
        elif type(response[key]) == list:
            for sent in response[key]:
                text += sent + ' '
            text += '\n\n'
        else:
            text += f'{response[key]}\n\n'
    return text

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_doc')
    args = parser.parse_args()
    response = parse_gpt_response(json.load(open(args.input_doc)))
    print(response)