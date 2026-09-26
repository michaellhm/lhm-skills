#!/usr/bin/env python3
"""Read-only per-run source client; authentication remains inside Hermes."""
import argparse,json,os,socket

def request(value):
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(os.environ['LHM_WEB_SOURCE_SOCKET']);s.sendall(json.dumps(value).encode()+b'\n');s.shutdown(socket.SHUT_WR)
        data=bytearray()
        while chunk:=s.recv(65536):data.extend(chunk)
    result=json.loads(data)
    if not result.get('ok'):raise RuntimeError(result.get('error','Source read failed'))
    return result['result']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['vault-list','vault-read','gmail-search','gmail-get']);p.add_argument('value',nargs='?',default='20 Clients');p.add_argument('--max',type=int,default=10);a=p.parse_args()
    print(json.dumps(request({'action':a.action,'value':a.value,'max':a.max}),ensure_ascii=False))
