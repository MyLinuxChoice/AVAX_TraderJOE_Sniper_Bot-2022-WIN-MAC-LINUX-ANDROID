from txns import TXN
import argparse, json
from time import sleep
from halo import Halo
from style import style

ascii = """

                                  ____.               
_____ ___  _______  ___  ___     |    | ____   ____   
\__  \\  \/ /\__  \ \  \/  /     |    |/  _ \_/ __ \  
 / __ \\   /  / __ \_>    <  /\__|    (  <_> )  ___/  
(____  /\_/  (____  /__/\_ \ \________|\____/ \___  > 
     \/           \/      \/                      \/  
           
"""

parser = argparse.ArgumentParser(description='Set your Token and Amount example: "sniper.py -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3 -a 0.2 -s 15"')
parser.add_argument('-t', '--token', help='str, Token for snipe e.g. "-t 0x34faa80fec0233e045ed4737cc152a71e490e2e3"')
parser.add_argument('-a', '--amount',default=0, help='float, Amount in AVAX to snipe e.g. "-a 0.1"')
parser.add_argument('-tx', '--txamount', default=1, nargs="?", const=1, type=int, help='int, how mutch tx you want to send? It Split your AVAX Amount in e.g. "-tx 5"')
parser.add_argument('-hp', '--honeypot', action="store_true", help='Check if your token to buy is a Honeypot, e.g. "-hp" or "--honeypot"')
parser.add_argument('-nb', '--nobuy', action="store_true", help='No Buy, Skipp buy, if you want to use only TakeProfit/StopLoss/TrailingStopLoss')
parser.add_argument('-tp', '--takeprofit', default=0, nargs="?", const=True, type=int, help='int, Percentage TakeProfit from your input AVAX amount "-tp 50" ')
parser.add_argument('-sl', '--stoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Stop loss from your input AVAX amount "-sl 50" ')
parser.add_argument('-tsl', '--trailingstoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Trailing-Stop-loss from your first Quote "-tsl 50" ')
parser.add_argument('-wb', '--awaitBlocks', default=0, nargs="?", const=True, type=int, help='int, Await Blocks before sending BUY Transaction "-ab 50" ')
parser.add_argument('-so', '--sellonly',  action="store_true", help='Sell all your Tokens from given address')
parser.add_argument('-bo', '--buyonly',  action="store_true", help='Buy Tokens with from your given amount')
parser.add_argument('-dsec', '--DisabledSwapEnabledCheck',  action="store_true", help='this argument disabled the SwapEnabled Check!')
args = parser.parse_args()


class SniperBot():

    def __init__(self):
        self.parseArgs()
        self.settings = self.loadSettings()
        self.SayWelcome()
    
    def loadSettings(self):
        with open("Settings.json","r") as settings:
            settings = json.load(settings)
        return settings

    def SayWelcome(self):
        print(style().YELLOW + ascii+ style().RESET)
        print(style().GREEN +"""Attention, You pay a 0.7% Tax on your swap amount!"""+ style().RESET)
        print(style().GREEN +"Start Sniper Tool with following arguments:"+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        print(style().YELLOW + "Amount for Buy:",style().GREEN + str(self.amount) + " AVAX"+ style().RESET)
        print(style().YELLOW + "Token to Interact :",style().GREEN + str(self.token) + style().RESET)
        print(style().YELLOW + "Transaction to send:",style().GREEN + str(self.tx)+ style().RESET)
        print(style().YELLOW + "Amount per transaction :",style().GREEN + str("{0:.8f}".format(self.amountForSnipe))+ style().RESET)
        print(style().YELLOW + "Await Blocks before buy :",style().GREEN + str(self.wb)+ style().RESET)

        if self.tsl != 0:
            print(style().YELLOW + "Trailing Stop loss Percent :",style().GREEN + str(self.tsl)+ style().RESET)
        if self.tp != 0:
            print(style().YELLOW + "Take Profit Percent :",style().GREEN + str(self.tp)+ style().RESET)
        if self.sl != 0:
            print(style().YELLOW + "Stop loss Percent :",style().GREEN + str(self.sl)+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        
    def parseArgs(self):
        self.token = args.token
        if self.token == None:
            print(style.RED+"Please Check your Token argument e.g. -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3")
            print("exit!")
            raise SystemExit

        self.amount = args.amount
        if args.nobuy != True:  
            if not args.sellonly: 
                if self.amount == 0:
                    print(style.RED+"Please Check your Amount argument e.g. -a 0.01")
                    print("exit!")
                    raise SystemExit

        self.tx = args.txamount
        self.amountForSnipe = float(self.amount) / float(self.tx)
        self.hp = args.honeypot
        self.wb = args.awaitBlocks
        self.tp = args.takeprofit
        self.sl = args.stoploss 
        self.tsl = args.trailingstoploss
        self.stoploss = 0
        self.takeProfitOutput = 0


    def calcProfit(self):
        if self.amountForSnipe == 0.0:
            self.amountForSnipe = self.TXN.getOutputfromTokentoAVAX()[0] / (10**18)

        a = ((self.amountForSnipe * self.tx) * self.tp) / 100
        b = a + (self.amountForSnipe * self.tx)
        return b 
    

    def calcloss(self):
        if self.amountForSnipe == 0.0:
            self.amountForSnipe = self.TXN.getOutputfromTokentoAVAX()[0] / (10**18)

        a = ((self.amountForSnipe * self.tx) * self.sl) / 100
        b = (self.amountForSnipe * self.tx) - a
        return b 


    def calcNewTrailingStop(self, currentPrice):
        a = (currentPrice  * self.tsl) / 100
        b = currentPrice - a
        return b


    def awaitBuy(self):
        spinner = Halo(text='await Buy', spinner='dots')
        spinner.start()
        for i in range(self.tx):
            spinner.start()
            self.TXN = TXN(self.token, self.amountForSnipe)
            tx = self.TXN.buy_token()
            spinner.stop()
            print(tx[1])
            if tx[0] != True:
                raise SystemExit


    def awaitSell(self):
        spinner = Halo(text='await Sell', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.sell_tokens()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 



    def awaitApprove(self):
        spinner = Halo(text='await Approve', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.approve()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 



    def awaitBlocks(self):
        spinner = Halo(text='await Blocks', spinner='dots')
        spinner.start()
        waitForBlock = self.TXN.getBlockHigh() + self.wb
        while True:
            sleep(0.13)
            if self.TXN.getBlockHigh() > waitForBlock:
                spinner.stop()
                break
        print(style().GREEN+"[DONE] Wait Blocks finish!")
        


    def awaitLiquidity(self):
        spinner = Halo(text='await Liquidity', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                self.TXN.getOutputfromAVAXtoToken()[0]
                spinner.stop()
                break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().GREEN+"[DONE] Liquidity is Added!"+ style().RESET)


    def fetchLiquidity(self):
        liq = self.TXN.getLiquidityAVAX()[1]
        print(style().GREEN+"[LIQUIDTY] Current Token Liquidity:",round(liq,3),"AVAX"+ style().RESET)
        if float(liq) < float(self.settings["MinLiquidityAVAX"]):
            print(style().RED+"[LIQUIDTY] TO SMALL LIQUIDITY, Exiting!"+ style().RESET)
            raise SystemExit
        return True


    def awaitEnabledBuy(self):
        spinner = Halo(text='await Dev Enables Swapping', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                if self.TXN.checkifTokenBuyDisabled() == True:
                    spinner.stop()
                    break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().GREEN+"[DONE] Swapping is Enabeld!"+ style().RESET)
    

    def awaitMangePosition(self):
        highestLastPrice = 0
        if self.tp != 0:
            self.takeProfitOutput = self.calcProfit()
        if self.sl != 0:
            self.stoploss = self.calcloss()
        TokenBalance = round(self.TXN.get_token_balance(),5)
        while True:
            try:
                sleep(0.3)
                LastPrice = float(self.TXN.getOutputfromTokentoAVAX()[0] / (10**18))
                if self.tsl != 0:
                    if LastPrice > highestLastPrice:
                        highestLastPrice = LastPrice
                        TrailingStopLoss = self.calcNewTrailingStop(LastPrice)
                    if LastPrice < TrailingStopLoss:
                        print(style().GREEN+"[TRAILING STOP LOSS] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break

                if self.takeProfitOutput != 0:
                    if LastPrice >= self.takeProfitOutput:
                        print()
                        print(style().GREEN+"[TAKE PROFIT] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break

                if self.stoploss != 0:
                    if LastPrice <= self.stoploss:
                        print()
                        print(style().GREEN+"[STOP LOSS] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break
                    
                msg = str("Token Balance: " + str("{0:.5f}".format(TokenBalance)) + "| CurrentOutput: "+str("{0:.7f}".format(LastPrice))+"AVAX")
                if self.stoploss != 0:
                    msg = msg + "| Stop loss below: " + str("{0:.7f}".format(self.stoploss)) + "AVAX"
                if self.takeProfitOutput != 0:
                    msg = msg + "| Take Profit Over: " + str("{0:.7f}".format(self.takeProfitOutput)) + "AVAX"
                if self.tsl != 0:  
                    msg = msg + "| Trailing Stop loss below: " + str("{0:.7f}".format(TrailingStopLoss)) + "AVAX"
                print(msg, end="\r")
            except Exception as e:
                print(e)
                sleep(5)
        print(style().GREEN+"[DONE] Position Manager Finished!"+ style().RESET)


    def StartUP(self):
        self.TXN = TXN(self.token, self.amountForSnipe)

        if args.sellonly:
            print("Start SellOnly, Selling Now all tokens!")
            inp = input("please confirm y/n\n")
            if inp.lower() == "y": 
                print("Wait for Liquidity?")
                liqq = input("please confirm y/n\n")
                if liqq.lower() == "y":
                    self.awaitEnabledBuy()
                print(self.TXN.sell_tokens()[1])
                raise SystemExit
            else:
                raise SystemExit

        if args.buyonly:
            print(f"Start BuyOnly, buy now with {self.amountForSnipe}AVAX tokens!")
            print(self.TXN.buy_token()[1])
            raise SystemExit

        if args.nobuy != True:
            self.awaitLiquidity()
            if args.DisabledSwapEnabledCheck != True:
                self.awaitEnabledBuy()

        honeyTax = self.TXN.checkToken()
        if self.hp == True:
            print(style().YELLOW +"Checking Token is Honeypot..." + style().RESET)
            if honeyTax[2] == True:
                print(style.RED + "Token is Honeypot, exiting")
                raise SystemExit

            elif honeyTax[2] == False:
                print(style().GREEN +"[DONE] Token is NOT a Honeypot!" + style().RESET)

        if honeyTax[1] > self.settings["MaxSellTax"]:
            print(style().RED+"Token SellTax exceeds Settings.json, exiting!")
            raise SystemExit

        if honeyTax[0] > self.settings["MaxBuyTax"]:
            print(style().RED+"Token BuyTax exceeds Settings.json, exiting!")
            raise SystemExit

        if self.wb != 0: 
            self.awaitBlocks()

        if self.fetchLiquidity():
            if args.nobuy != True:
                self.awaitBuy()

        sleep(7) # Give the RPC/WS some time to Index your address nonce, make it higher if " ValueError: {'code': -32000, 'message': 'nonce too low'} "
        self.awaitApprove()

        if self.tsl != 0 or self.tp != 0 or self.sl != 0:
            self.awaitMangePosition()

        print(style().GREEN + "[DONE] AVAX JOE Sniper Bot finish!" + style().RESET)

SniperBot().StartUP()
