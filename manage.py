#!/usr/bin/env python
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BACKEND=ROOT/'web'/'backend'
APPS=BACKEND/'x2dhf_project'
sys.path.insert(0,str(BACKEND))
sys.path.insert(0,str(APPS))
os.chdir(BACKEND)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','x2dhf_project.settings')
os.environ.setdefault('X2DHF_DIRECTORY',str(ROOT))
os.environ.setdefault('X2DHF_BINARY_PATH',str(ROOT/'bin'/'xhf'))

if __name__=='__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
