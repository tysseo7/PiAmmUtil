import requests
import sys
args = sys.argv
#adr = args[1]
#ISS   = args[2]
HORIZON_URL="https://api.testnet.minepi.com"
POOL_ID = {
  "1838e29e36a35b82f1dfbe9d1d00471616eb5a08fdf14b2899b159061d5212b4": "Archimedes",
  "608e1be624afb95a5f316abaa25981fcf3dbc1b7881b9af365a032440f5ee3ba": "PizzaToken",
  "b20eaf06c591202c75cf2f5649d4d0f5c9274c998b1dabc682b42140765c18f8": "ShrimpSwap",
  "709fdccdd88e0d4a612536ef2604683226165b7c8ddd81980963aaf3f0a2ab8f": "BALL"
}
def inverse_dic(dictionary):
	return {v:k for k,v in dictionary.items()}
INV_PID=inverse_dic(POOL_ID)
#print(INV_PID)


def getPrice(hurl,token):
  pid=INV_PID[token]
  url=f"{hurl}/liquidity_pools/{pid}"
  resp = requests.get(url).json()
  #code = POOL_ID[pid]
  #print(resp)
  #tlsh    = float(resp['total_shares'])
  #tres_a  = float(resp['reserves'][0]['amount'])
  #balance = tres_a / tlsh * mysh * 2
  rate    = float(resp['reserves'][0]['amount']) / float(resp['reserves'][1]['amount'])
  return rate



def share2native(hurl,a,token):
  url=f"{hurl}/accounts/{a}"
  resp = requests.get(url).json()
  #print(resp["balances"])
  for bb in resp["balances"]:
    #print(f"INV_PID[token]: {INV_PID[token]}")
    if "liquidity_pool_id" in bb :
      if bb["liquidity_pool_id"] == INV_PID[token] :
        url2 = f"{hurl}/liquidity_pools/{INV_PID[token]}"
        res2 = requests.get(url2).json()
        #print(bb)
        #print(bb['balance'])
        #print(token)
        #print(res2['reserves'][0])
        my_shares = float(bb['balance'])
        total_shares = float(res2['total_shares'])
        if res2['reserves'][0]['asset'] == 'native':
          rev0 = float(res2['reserves'][0]['amount'])
          rev1 = float(res2['reserves'][1]['amount'])
          rate = rev0 / rev1
          my_rev0 = rev0 / total_shares * my_shares 
          #print(rate)
          #print(my_rev0)
          #print(my_rev0*2)
          #exit()
          return my_rev0*2 , rate
        else :
          return -3.14 , 3.14

    #if bb in "quidity_pool_id" :
      #print(f"liquidity_pool_id: {bb['liquidity_pool_id']}")
  exit()

def getBlance(hurl,a):
  print(f"\n address: {a[0]}{a[1]}{a[2]}{a[3]}")
  print("------------------------------------")
  t_b = 0.0
  url=f"{hurl}/accounts/{a}"
  #print(url)
  resp = requests.get(url).json()
  #print(resp)
  bb   = resp["balances"]
  #print(bb)
  for bl in bb:
    #print(f"{bl['balance']}, {bl['asset_type']}")
    type = bl['asset_type']
    blnc = float(bl['balance'])
    #print(type(blnc))
    if type == "native":
      print(f"{blnc:10.2f} TestPi")
      t_b+=blnc
    else:
      if type == "liquidity_pool_shares":
        #print(f"{blnc}	shares")
        b,c,r,m = share2pi(blnc,hurl,bl['liquidity_pool_id'])
        if b==0:
          amo_token=0
        else:
          amo_token=(b/2)/r
        print(f"{b:10.2f} TestPi ({amo_token:9.4f} {c}-p ) rate:{r:10.2f}  [ pool_sh={m:7.2f} ]")
        t_b+=b
      else:
        #print(bl)
        b,c,r,m = share2pi(blnc,hurl,INV_PID[bl['asset_code']])
        b2=r*blnc
        print(f"{b2:10.2f} TestPi ({blnc:9.4f} {c}   ) rate:{r:10.2f}")
        t_b+=b2
  print("------------------------------------")
  print(f"Total :\n{t_b:10.2f} TestPi")

   
def share2pi(mysh,hurl,pid):
  url=f"{hurl}/liquidity_pools/{pid}"
  resp = requests.get(url).json()
  code = POOL_ID[pid]
  #print(resp)
  tlsh    = float(resp['total_shares'])
  tres_a  = float(resp['reserves'][0]['amount'])
  balance = tres_a / tlsh * mysh * 2
  rate    = float(resp['reserves'][0]['amount']) / float(resp['reserves'][1]['amount'])
  
  #print(POOL_ID)
  #print(f"{balance}	in pool:{code}: my_shares {mysh} rate:{rate}")
  if code == "BALL":
    code ="      BALL"
  return balance, code, rate, mysh

     

'''
adr = "GDVWOYCULBEYT7TKGZKAO5R4HDOL3MNTJLB2MXZ76CQNUF6KN4HHHMAW"
getBlance(HORIZON_URL,adr)
adr = "GB3FNPGWTKWF3T5PCBMDJZRYRPE6PVMANMZOZMXDHWN5YFAOVNBKFQQG"
getBlance(HORIZON_URL,adr)
'''

