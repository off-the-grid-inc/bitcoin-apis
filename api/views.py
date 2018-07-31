# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from TXtool import *
from ECbitcoin import *

# Create your views here.

def home(request):
	return render(request, 'homepage.html')

def prepare_signature(request):
	s_address = str(request.GET.get("sender", None))
	receiver = request.GET.get("receiver", None)
	amount = int(request.GET.get("amount", None))
	fee = int(request.GET.get("fee", None))
	tx = quick_unsigned_tx(s_address, receiver, amount, fee)
	if tx==-1:
		raise ValueError
	raw_hashes = prepare_sig(tx, s_address)
	hashes = [i.encode('hex') for i in raw_hashes]
	success = 'success!'
	data = {'hashes': hashes, 'success':success, 'unsigned': tx}
	return JsonResponse(data)

def create_testwallet(request):
	priv, pt = genECkeypair()
	address = convertPub2Addr(convertPt2Pub(pt), testnet=True)
	unsigned = quick_unsigned_tx("mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy", address, btc2sat(.05), 5000)
	raw_hashes = prepare_sig(unsigned, "mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy")
	raw_sigs = [ECsign(int(i.encode('hex'),16), T1) for i in raw_hashes]
	btc_format = [rawSig2ScriptSig(i, TP) for i in raw_sigs]
	tx = apply_sig(unsigned, btc_format)
	r = pushTX(tx, testnet=True)
	if r['status'] == 'success':
		hp = hex(priv)
		hp = hp[:-1] if hp[-1]=='L' else hp
		data = {'tx': r['data']['txid'], 'address': address, 'priv': hp[2:]}
		return JsonResponse(data)
	raise ValueError
	




