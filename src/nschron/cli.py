import argparse
import json
from dataclasses import asdict
from .core import convert,parse_inscription

def main():
    parser=argparse.ArgumentParser(description='Experimental Malla-era Nepal Sambat date candidate finder')
    parser.add_argument('inscription',nargs='+',help='e.g. NS 822 Asada Sukla 15 Friday')
    parser.add_argument('--adhika',choices=['yes','no','any'],default='any')
    args=parser.parse_args()
    try:
        query=parse_inscription(' '.join(args.inscription))
        leap={'yes':True,'no':False,'any':None}[args.adhika]
        result=convert(**query,intercalary=leap)
        print(json.dumps(dict(query=query, candidates=[asdict(v) for v in result],
                              count=len(result)),indent=2,ensure_ascii=False))
    except (ValueError,RuntimeError) as exc: parser.error(str(exc))
if __name__=='__main__':main()
