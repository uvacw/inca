# -*- coding: utf-8 -*-
from core.processor_class import Processer
import logging
import re
from colorama import init
from colorama import Fore
from colorama import Style

init()

logger = logging.getLogger(__name__)



def _annotate(text, key, question, highlight_regexp, window=150, display=True):
    '''prompts for annotation'''
    if display == True:
        print('\n',Fore.RED,'Please annotate the following text:')
        if highlight_regexp == None:
            print(Style.RESET_ALL,text)
        else:
            print(Fore.RED+'(only excerpts are shown)'+Style.RESET_ALL)
            reststring = text
            numberofmatches=len(re.findall(highlight_regexp,text))
            poscount=0
            for i in range(numberofmatches):
                #print('Occurance {} of {}'.format(i+1,numberofmatches))
                r=re.search(highlight_regexp,reststring)
                print(poscount)
                if poscount+r.start() < window:
                    print(text[poscount:poscount+r.start()], end='')
                    print(Fore.GREEN+text[poscount+r.start():poscount+r.end()], end='')
                    print(Style.RESET_ALL + text[poscount+r.end():poscount+r.end()+window])
                else:
                    print(text[poscount+r.start()-window:poscount+r.start()], end='')
                    print(Fore.GREEN+text[poscount+r.start():poscount+r.end()], end='')
                    print(Style.RESET_ALL + text[poscount+r.end():poscount+r.end()+window])
                reststring=reststring[r.end():]
                poscount+=r.end()
    
    answer=input(Fore.RED + question + Style.RESET_ALL)
    return answer


class annotate(Processer):
    '''Adds human annotations'''

    def process(self, document_field, highlight_regexp = None, questions = {'relevance':'Is this relevant?'}, window=150):
        '''human annotations'''

        while True:
            annotations = {}
            display=True
            for key, question in questions.items():
                annotations[key] = _annotate(document_field,key,question, highlight_regexp, window=window, display=display)
                display=False
            print(Fore.RED+'You annotated this document as follows:'+Style.RESET_ALL)
            print(annotations)
            confirm = input(Fore.RED+'\nIs this correct? [Y/N]')
            if confirm.strip().lower()=='y':
                return annotations
    
