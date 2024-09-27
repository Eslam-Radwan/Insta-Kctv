from pprint import pprint
import logging
logger = logging.getLogger(__name__)


internal_representation =  {"Section N": {
                        "Title": "TITLE",
                        "Figures": [
                            {"Name": "Figure K", "Caption": "CAPTION"},
                             {"Name": "Figure K", "Caption": "CAPTION"}
                        ],
                        "Content": [
                        "SENT",
                        "SENT"
                        ]
                        },
                        "Section N": {
                        "Title": "TITLE",
                        "Figures": [
                            {"Name": "Figure K", "Caption": "CAPTION"},
                            {"Name": "Figure K", "Caption": "CAPTION"}
                        ],
                        "Content": [
                        "SENT",
                        "SENT"
                        ]
                        },
                        }


internal_representation_no_figures =  '''{
                        "Document Title": "TITLE",
                        "Document Authors: ["AUTHOR 1", "AUTHOR2", ... "AUTHOR N"]
                        "SECTION TITLE 1": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },
                        "SECTION TITLE 2": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },...   
                         "SECTION TITLE N": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        }
                        }'''

headers_only =  '''[ SECTION TITLE 1, SECTION TITLE 2, .... SECTION TITLE N]'''
