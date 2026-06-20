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
logger = logging.getLogger(__name__)

def replace_mentions_of_figures(latex, figure_dir, output_dir=None, template_type=None):
    if figure_dir is None:
        return latex
        
    replaced_figures = set()
    
    def replace_gfx(match):
        fig_type = match.group(2)
        fig_num = match.group(3)
        fig_paths = glob.glob(os.path.join(figure_dir, f"*{fig_type}{fig_num}-*.png"))
        if fig_paths:
            f_path = fig_paths[0]
            replaced_figures.add((fig_type.lower(), int(fig_num)))
            if output_dir:
                insert_path = os.path.relpath(f_path, output_dir).replace('\\', '/')
            else:
                insert_path = f_path.replace('\\', '/')
            options = match.group(1) or ""
            return f"\\includegraphics{options}{{{insert_path}}}"
        return match.group(0)
        
    # Match: \includegraphics[options]{...Figure/Table X...}
    pattern = r"\\includegraphics(\[.*?\])?\{.*?(Figure|Table)\s*(\d+).*?\}"
    latex = re.sub(pattern, replace_gfx, latex, flags=re.IGNORECASE)
    
    paragraphs = latex.split('\n\n')
    inserted = len(replaced_figures) > 0
    
    for i, paragraph in enumerate(paragraphs):
        figures = re.findall("(Figure|Table) (\d+)", paragraph)
        for fig_type, fig_num in figures:
            if (fig_type.lower(), int(fig_num)) in replaced_figures:
                continue
                
            fig_paths = glob.glob(os.path.join(figure_dir, f"*{fig_type}{fig_num}-*.png"))
            if fig_paths:
                for f_path in fig_paths:
                    logger.info(f'Inserting Figure {f_path}')
                    inserted = True
                    if output_dir:
                        insert_path = os.path.relpath(f_path, output_dir).replace('\\', '/')
                    else:
                        insert_path = f_path.replace('\\', '/')
                    
                    if template_type == 'slide':
                        options = 'width=0.8\\textwidth,height=0.5\\textheight,keepaspectratio'
                    elif template_type == 'poster':
                        options = 'width=\\linewidth'
                    elif template_type == 'blog':
                        options = 'width=0.8\\textwidth'
                    else:
                        options = ''
                        
                    if options:
                        gfx_str = f"\\includegraphics[{options}]{{{insert_path}}}"
                    else:
                        gfx_str = f"\\includegraphics{{{insert_path}}}"
                        
                    # Find the first end environment to insert before
                    insert_idx = -1
                    for env in ["\\end{block}", "\\end{frame}", "\\end{document}"]:
                        idx = paragraph.rfind(env)
                        if idx != -1:
                            insert_idx = idx
                            break
                            
                    if insert_idx != -1:
                        paragraph = paragraph[:insert_idx] + gfx_str + "\n" + paragraph[insert_idx:]
                    else:
                        paragraph += f'\n{gfx_str}'
        paragraphs[i] = paragraph
    
    result = "\n\n".join(paragraphs)
    if inserted:
        if "\\usepackage{graphicx}" not in result:
            idx = result.find("\\begin{document}")
            if idx != -1:
                result = result[:idx] + "\\usepackage{graphicx}\n" + result[idx:]
        if "\\usepackage{float}" not in result:
            idx = result.find("\\begin{document}")
            if idx != -1:
                result = result[:idx] + "\\usepackage{float}\n" + result[idx:]
                
    return result

def strip_code_fence(text):
    if text.startswith('```'):
        first_newline = text.find('\n')
        last_newline = text.rfind('\n```')
        if last_newline != -1:
            return text[first_newline+1:last_newline]
    return text

def main(args):
    # Take input doc 
    input_json = data.get_data(args.input_doc, args.output_dir)['content']

    output_doc_name = args.input_doc.split('/')[-1].split('.')[0]
    os.makedirs(args.output_dir, exist_ok=True)

    if args.figures_dir is None:
        auto_figures_dir = os.path.join(os.path.dirname(os.path.abspath(args.input_doc)), 'figures')
        if os.path.isdir(auto_figures_dir):
            logger.info(f"Automatically detected figures directory: {auto_figures_dir}")
            args.figures_dir = auto_figures_dir

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
            template = templates.internal_representation if args.figures_dir else templates.internal_representation_no_figures
            prompt = prompts.sure_prompt.format(template, input_json)
            test_prompt = [{"role": "user", "content":  prompt}]

        gpt_response = gpt.get_response(args.model_name, test_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        if args.text_of_internal_rep:
            try:
                json_repsonse = json.loads(gpt_response)
                gpt_response = data.parse_gpt_response(json_repsonse).strip()
            except json.JSONDecodeError:
                # Skip parsing non valid jsons
                pass


        gpt_response = strip_code_fence(gpt_response)
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
        gpt_latex = gpt.get_response(args.model_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = strip_code_fence(gpt_latex)
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.figures_dir, args.output_dir, template_type='slide')
        with open(os.path.join(args.output_dir, f'{output_doc_name}_slides.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

    # Poster
    if args.which_template == 'poster' or args.which_template == 'all':
        logger.info(f'Creating poster...')
        if args.no_style_param:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex_no_style.format('beamer poster', gpt_response)}]
        else:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex.format('beamer poster', style.posters, gpt_response)}]
        gpt_latex = gpt.get_response(args.model_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = strip_code_fence(gpt_latex)
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.figures_dir, args.output_dir, template_type='poster')
        with open(os.path.join(args.output_dir, f'{output_doc_name}_poster.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

    # Blog post
    if args.which_template == 'blog' or args.which_template == 'all':
        logger.info(f'Creating blog post...')
        if args.no_style_param:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex_no_style.format('blog post', gpt_response)}]
        else:
            latex_prompt = [{'role': 'user', 'content': prompts.convert_to_latex.format('blog post', style.blogs, gpt_response)}]
        gpt_latex = gpt.get_response(args.model_name, latex_prompt, temperature=args.temperature, time_wait=time_wait)['choices'][0]['message']['content']
        gpt_latex = strip_code_fence(gpt_latex)
        gpt_latex = replace_mentions_of_figures(gpt_latex, args.figures_dir, args.output_dir, template_type='blog')
        with open(os.path.join(args.output_dir, f'{output_doc_name}_blog.tex'), 'w', encoding='utf-8') as fout:
            fout.write(gpt_latex)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_doc')
    parser.add_argument('output_dir')
    parser.add_argument('--model-name', default=os.getenv("OPENAI_MODEL_NAME", "openai/gpt-oss-20b:free"))
    parser.add_argument('--max-req-per-min', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--which-template', default='all', choices=['poster', 'blog', 'slides', 'all', 'none'])
    parser.add_argument('--skip-internal-rep', action='store_true', default=False)
    parser.add_argument('--text-of-internal-rep', action='store_true', default=False)
    parser.add_argument('--sure-no-template', action='store_true', default=False)
    parser.add_argument('--no-style-param', action='store_true', default=False)
    parser.add_argument('--figures-dir', default=None, help='Directory containing pdffigures2 extracted figure PNGs. If omitted, figure insertion is skipped.')
    parser.add_argument('--specify-length', default=None, help='Comma separated range of desired length, e.g.\"500,1000\"')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    main(args)

