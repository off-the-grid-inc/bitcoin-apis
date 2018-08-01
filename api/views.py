# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from models import DemoAddress
import random
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

def get_testwallet(request):
	demo_wallet = random.choice(DemoAddress.objects.all())
	data = {'address': data.address, 'priv':data.privkey, 'pub':data.pubkey}
	return JsonResponse(data)

def fund_wallets(request):
	j = 0
	while j < 4:
		try:
			priv, pt = genECkeypair()
			address = convertPub2Addr(convertPt2Pub(pt), testnet=True)
			unsigned = quick_unsigned_tx("mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy", address, btc2sat(0.25), 3000)
			raw_hashes = prepare_sig(unsigned, "mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy")
			raw_sigs = [ECsign(int(i.encode('hex'),16), T1) for i in raw_hashes]
			btc_format = [rawSig2ScriptSig(i, TP) for i in raw_sigs]
			tx = apply_sig(unsigned, btc_format)
			r = pushTX(tx, testnet=True)
			if r['status'] == 'success':
				hp = hex(priv)
				hp = hp[2:-1] if hp[-1]=='L' else hp[2:]
				pub = convertPt2Pub(pt)
				a = DemoAddress()
				a.address = address
				a.pubkey = pub
				a.privkey = hp
				a.save()
		except:
			pass
		j += 1
		time.sleep(.3)
	data = {'status:', '4 new wallets created'}
	return JsonResponse(data)
	




