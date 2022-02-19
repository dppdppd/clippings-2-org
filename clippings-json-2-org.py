# -*- coding: utf-8 -*-


import os
import sys
import logging
from dateutil import parser
import argparse
from datetime import datetime
import time
import shortuuid
import uuid
import re
import glob
import json

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")

argParser = argparse.ArgumentParser(description = 'Convert clippings.io json to org')
argParser.add_argument('-d', '--dir', type=dir_path, default=os.getcwd(), help='Directory to process')
argParser.add_argument('-o', '--outdir', type=dir_path, default=os.getcwd(), help='Directory to output')
args = argParser.parse_args()

ORG_TIMESTAMP_FORMAT = '[%Y-%m-%d %a %H:%M:%S]'


  # {
  #   "BookTitle": "The Cambridge World History of Slavery: Volume 1, The Ancient Mediterranean World",
  #   "BookAuthor": "Keith Bradley and Paul Cartledge",
  #   "Content": "put slave figures at around 15 per cent of the total population,",
  #   "Location": "1703",
  #   "Page": "",
  #   "CreatedKindle": "2021-11-18T08:00:00",
  #   "CreatedWebsite": "2022-02-18T06:22:42.483",
  #   "AnnotationType": "Highlight"
  # },

print( args.dir )
for file in os.listdir(args.dir):
    if not file.endswith('.json'):
        continue

    with open(os.path.join( args.dir, file), 'r') as f:
        of = json.load(f)

        outbuf = ''
        outbuf += f'#+TITLE: {of[0]["BookTitle"]}\n'
        outbuf += f'#+AUTHOR: {of[0]["BookAuthor"]}\n'
        outbuf += '\n'

        for hl in of:
            created_ts = parser.parse(hl["CreatedKindle"]).timestamp()
            org_ts = datetime.fromtimestamp( created_ts ).strftime( ORG_TIMESTAMP_FORMAT )

            tagstr = ''
            if 'Tags' in hl:
                tagstr += '    :'
                for tag in hl['Tags']:
                    tagstr += tag + ':'

            outbuf += f'* {hl["AnnotationType"]}: {hl["Content"][:50]}{tagstr}\n'
            outbuf += f':PROPERTIES:\n'
            outbuf += f':CREATED: {org_ts}\n'

            outbuf += f':TITLE: {hl["BookTitle"]}\n'
            outbuf += f':AUTHOR: {hl["BookAuthor"]}\n'

            if hl["Location"]:
                outbuf += f':LOCATION: {hl["Location"]}\n'

            if hl["Page"]:
                outbuf += f':PAGE: {hl["Page"]}\n'

            outbuf += f':ID: {uuid.uuid5( uuid.NAMESPACE_URL, hl["Location"] + hl["CreatedKindle"] )}\n'
            outbuf += f':END:'

            outbuf += '\n'
            outbuf += f'{hl["Content"]}\n'

            if 'Notes' in hl:
                for note in hl["Notes"]:
                    outbuf += f'** Note\n'
                    outbuf += f'{note}\n'

            outbuf += '\n'

    created_ts = parser.parse(of[0]["CreatedKindle"]).timestamp()
    date_prefix = datetime.fromtimestamp( created_ts ).strftime( '%Y%m%d - ' )

    with open(os.path.join( args.outdir, date_prefix + file.replace('.json','.org') ), "w") as f:
        f.write(outbuf)
