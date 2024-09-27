import gpt
import prompts
import json
import argparse
import data
import style
import logging
import templates
import os
import time
import glob
import re
from pprint import pprint

def replace_mentions_of_figures(latex, figure_dir):
    latex = latex.split('\n\n')
    for paragraph in latex:
        figures = re.findall("(Figure|Table) (\d+)", paragraph)
        for fig_type, fig_num in figures:
            fig_paths = glob.glob(os.path.join(figure_dir, f"fig_*-{fig_type}{fig_num}-*.png"))
            if fig_paths:
                for f_path in fig_paths:
                    logger.info(f'Inserting Figure {f_path}')
                    paragraph += '\n\includegraphics{%s}'.format(f_path)
    return "\n\n".join(latex)


def main(args):
    # Take input doc 
    input_json = data.get_data(args.input_doc, args.output_dir)['content']

    os.makedirs(args.output_dir, exist_ok=True)
    output_doc_name = args.input_doc.split('/')[-1].split('.')[0]

    time_wait = 60 / args.max_req_per_min

    if args.skip_internal_rep:
        gpt_response = input_json
    else:
        # Call GPT
        if args.sure_no_template:
            prompt = prompts.sure_prompt_no_template.format(input_json)
            test_prompt = [{"role": "user", "content":  prompt}]
            #print(test_prompt)
        else:
            prompt = prompts.sure_prompt.format(templates.internal_representation_no_figures, input_json)
            test_prompt = [{"role": "user", "content":  prompt}]

        gpt_response = gpt.get_response(args.model_name, args.service_name, test_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        if args.text_of_internal_rep:
            try:
                json_repsonse = json.loads(gpt_response)
                gpt_response = data.parse_gpt_response(json_repsonse).strip()
            except json.JSONDecodeError:
                # Skip parsing non valid jsons
                pass


        with open(os.path.join(args.output_dir, f'{output_doc_name}.json'), 'w', encoding='utf-8') as fout:
            try:
                json.dump(json.loads(gpt_response), fout, indent=4)
            except json.JSONDecodeError:
                fout.write(gpt_response)
    
    # Convert to latex
    if args.specify_length:
        x1, x2 = args.specify_length.split(',')
        if int(x1) == 0:
            spec_length = style.specify_length_0.format(x2)
        else:
            spec_length = style.specify_length.format(x1, x2)
    else:
        spec_length = ''

    # Slides
    if args.which_template == 'slides' or args.which_template == 'all':
        logger.info(f'Creating slides...')
        if args.no_style_param:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex_no_style.format('slide', gpt_response)}]
        else:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex.format('slide', style.slides, gpt_response)}]
        gpt_latex = gpt.get_response(args.model_name, args.service_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.output_dir)
        with open(os.path.join(args.output_dir, f'{output_doc_name}_slides.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

    # Poster
    if args.which_template == 'poster' or args.which_template == 'all':
        logger.info(f'Creating poster...')
        if args.no_style_param:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex_no_style.format('beamer poster', gpt_response)}]
        else:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex.format('beamer poster', style.posters, gpt_response)}]
        gpt_latex = gpt.get_response(args.model_name, args.service_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.output_dir)
        with open(os.path.join(args.output_dir, f'{output_doc_name}_poster.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

    # Blog post
    if args.which_template == 'blog' or args.which_template == 'all':
        logger.info(f'Creating blog post...')
        if args.no_style_param:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex_no_style.format('blog post', gpt_response)}]
        else:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex.format('blog post', style.blogs, gpt_response)}]
        gpt_latex = gpt.get_response(args.model_name, args.service_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.output_dir)
        with open(os.path.join(args.output_dir, f'{output_doc_name}_blog.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_doc')
    parser.add_argument('output_dir')
    parser.add_argument('--model-name', default="gpt35-16k")
    parser.add_argument('--service-name', default="azure")
    parser.add_argument('--max-req-per-min', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--which-template', default='all', choices=['poster', 'blog', 'slides', 'all', 'none'])
    parser.add_argument('--skip-internal-rep', action='store_true', default=False)
    parser.add_argument('--text-of-internal-rep', action='store_true', default=False)
    parser.add_argument('--sure-no-template', action='store_true', default=False)
    parser.add_argument('--no-style-param', action='store_true', default=False)
    parser.add_argument('--specify-length', default=None, help='Comma separated range of desired length, e.g.\"500,1000\"')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    main(args)

