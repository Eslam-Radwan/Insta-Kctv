'''
Contains style parameters for each template
'''

slides = '''
Slides should use a clean modern design, specifically the Metropolis theme (\\usetheme{metropolis}). 
Include a title page. Following slides should contain an informative slide title and short, concise bullet points.
Ensure you include \\usepackage{float} and \\usepackage{graphicx} in the preamble.
For any figure or table mentioned, insert a centered figure environment at the appropriate place on the slide:
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth,height=0.5\\textheight,keepaspectratio]{Figure X}
    \\caption{Caption of Figure X}
\\end{figure}
where X is the figure/table number.
'''   

posters = '''
Posters should include a title section at the top, and organize panels into a clean grid columns layout.
Each block/panel should include a heading and short, concise bullet points.
For any figure or table mentioned, insert a centered figure environment inside the block:
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=\\linewidth]{Figure X}
    \\caption{Caption of Figure X}
\\end{figure}
where X is the figure/table number. Ensure you load \\usepackage{float} and \\usepackage{graphicx} in the preamble.
'''   

blogs = '''
Blogs should include paragraphs introducing the topic, a summary of the input document, and important takeaways.
Use a clean LaTeX article format. Enhance the layout by adding \\usepackage{caption} and configuring it beautifully:
\\captionsetup{font=small,labelfont=bf,textfont=it,margin=10pt}
For any figure or table mentioned, insert a centered figure environment at the appropriate place:
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{Figure X}
    \\caption{Caption of Figure X}
\\end{figure}
where X is the figure/table number. Ensure you load \\usepackage{float} and \\usepackage{graphicx} in the preamble.
'''

specify_length = ' The output document should be between {} and {} words.'

specify_length_0 = ' The output document should be less than {} words.'
