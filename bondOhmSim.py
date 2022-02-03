import random
"""
Bond sim with the OHM model of issuing tokens for bonds
There's no tokens due to bond holders but the token price 
is now important for bond holders and users in general

NOTE
Token price suffers pretty hard here. Approaching 0 unless the
treasury actively dumps all profits into pumping it back up.
Tokens would need other utility or this would be complete ponzinomics
"""

# User class
class user:
    bondTokensDue = 0
    duePerPeriod = 0
    paymentsAmount = 0
    tokenBalance = 0
    def __init__(self, balance):
        self.balance = balance

# exchange token handles the token and the trading for it with ghetto liquidity pools. Slightly innacurate with LP adds but good enough
class exchangeToken:
    lpStableBalance = 0 #Amount of stablecoins (usd) in trading pool
    lpTokenBalance = 0  #Amount of tokens in the trading pool
    
    def __init__(self,initialLP):
        self.lpStableBalance += initialLP
        self.lpTokenBalance += initialLP
    
    def addLP(self, amountStable, amountToken):
        self.lpStableBalance += amountStable
        self.lpTokenBalance += amountToken

    def sell(self, amountToken):
        self.lpTokenBalance += amountToken
        returnedStable = self.getTokensOut(False,amountToken)
        self.lpStableBalance -= returnedStable
        return returnedStable

    def buy(self, amountStable):
        self.lpStableBalance += amountStable
        returnedToken = self.getTokensOut(True,amountStable)
        self.lpTokenBalance -= returnedToken
        return returnedToken

    def getTokensOut(self, isStableIn, inAm):
        if(isStableIn):
            return inAm * (self.lpStableBalance / self.lpTokenBalance)
        else:
            return inAm * (self.lpTokenBalance / self.lpStableBalance)

# treasury is the main class. Does the sim
class treasury:
    count = 0               #sim itteration
    total = 0               #total $ in treasury
    premium = 0.05          #bond premium (unused)
    swapAddition = 0.05     #extra % added to swap APR
    period = 10             #10 itterations in a bond lifecycle
    totalTokensBought = 0   #total tokens bought by the treasury in buybacks

    def __init__(self,users):
        self.users = users
        self.token = exchangeToken(10000)

    def buyBond(self, buyer, amountStable):
        toSwap = amountStable/2
        returned = self.token.sell(toSwap)
        self.token.addLP(toSwap,returned)
        amountToken = self.token.getTokensOut(True,amountStable)
        users[buyer].bondTokensDue += amountToken + amountToken * self.premium
        users[buyer].duePerPeriod += (amountToken + amountToken * self.premium) / self.period

    def buySwap(self, buyer, underlying):
        self.users[buyer].paymentsAmount = (underlying * (self.premium + self.swapAddition))/self.period

    def tick(self):
        for user in self.users:
            if(user.bondTokensDue > 0):
                user.tokenBalance += user.duePerPeriod
                user.bondTokensDue -= user.duePerPeriod

            self.total += user.paymentsAmount
            user.balance -= user.paymentsAmount
            user.balance += self.token.sell(user.tokenBalance)
            user.tokenBalance = 0

        print("\tPeriod",self.__incrementCount())
        
        print("Total:\t",self.total)
        print("Token Price:\t",self.token.getTokensOut(True,1))

    def __incrementCount(self):
        self.count = self.count+1
        return self.count

users = [user(1000),user(2000),user(4000)]

t = treasury(users)

propBuyBond = 5
probBuySwap = 5

for i in range(0,100):
    for j in range(0,3):

        if(random.randint(0,100) < propBuyBond):
            t.buyBond(j,200)
        elif(random.randint(0,100) < probBuySwap):
            t.buySwap(2,200)

    t.tick()

