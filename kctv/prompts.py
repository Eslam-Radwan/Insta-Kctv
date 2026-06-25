sure_prompt = f"Given the input text, extract the document title and authors."\
    "For each section in the given input text, extract the most important sentences."\
    "Format the output using the following json template:\n"\
    "{}\n\n" \
    "Input: {}\n" \
    "Output:"

sure_prompt_no_template = f"Given the input text, extract the document title and authors. "\
    "For each section in the given input text, extract the most important sentences. "\
    "Format the output in a structured format.\n"\
    "Input: {}\n" \
    "Output:"

## Include a short description of the document type (e.g. slides should include short bullet points)
## Make a few experiments with few shot examples 
## Section to slide - not paper to slides 
## Ask the model to rationalize why it chose to make the slide the way it did
## or why is the sentence important to extract 
convert_to_latex = "Summarize the following input in a {} style."\
                "Style parameters: {}"\
                "Format the output document as a latex file:\n"\
                "Input: {}\n\n"\
                "Output:"

convert_to_latex_no_style = "Summarize the following input in a {} style."\
                "Format the output document as a latex file:\n"\
                "Input: {}\n\n"\
                "Output:"
