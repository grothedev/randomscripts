#!/bin/python3

#from google import genai
import os
import argparse
import requests


API_KEY=os.getenv('GEMINI_API_KEY')
API_URL=f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}'
#client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

#todo make modular
def main():
    parser = argparse.ArgumentParser("gemini cli tool")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    parser_query = subparsers.add_parser('q', help='query the model')
    parser_query.add_argument('query', nargs='+', help='the query string')

    args = parser.parse_args()


    print(API_URL)

    if args.command == 'q':
        query_text = ' '.join(args.query)
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = { #todo options for other parameters
            "contents": [
                {
                    "parts": [
                        {
                            "text": query_text
                        }
                    ]
                }
            ]
        }
        
        #todo: also save the response to db
        httpResponse = requests.post(API_URL, headers=headers, json=data)
        json = httpResponse.json()
        response = json['candidates'][0]['content']['parts'][0]['text']

        print(response)
    return


if __name__ == '__main__':
    main()
