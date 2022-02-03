import random
import matplotlib.pyplot as plt

"""
    Share simulation. Shares are issued linearly each tick to build treasury
    Shares determine the dividends of swap income
    Half of all shares are always owned by treasury
    Half of all shares are sold on the market at valuation
    = treasury total / half of all shares (floating)
    Share valuation increases over time
    income per share decreases over time

    Idea here would be to have smart contracts calculate this valuation and only
    issue shares when overvalued
"""

#user class

class user:
    paymentsAmount = 0
    def __init__(self, balance):
        self.balance = balance

# treasury is the main class
class treasury:
    count = 0                   #sim itteration
    total = 0                   #total $ in treasury
    premium = 0.05              #premium accrues over periods linearly across periods
    swapAddition = 0.05         #extra % (on top of bond premium) added to swaps APR
    period = 10                 #periods of bond accrual of the premium
    swapsIssued = 0             #count of swaps issued
    totalTokenSupply = 0        #total supply of tokens
    newTokensEachTick = 10      #new tokens minted per tick
    underlyingExposed = 0       #underlying exposed to swaps and can't be used
    fundsRaised = 0             #total $ earned from token sales
    totalIncome = 0             #total income from swaps
    maxForIssue = 500000        #will stop issuing after this much in total treasury

    def __init__(self,users,startingPaddingTotal):
        self.total = startingPaddingTotal
        self.users = users

    # every tick issue some new tokens. Issue as many to self as to market to keep half of share
    def issueTokens(self):
        if(self.total < self.maxForIssue or self.maxForIssue == 0):
            self.totalTokenSupply += self.newTokensEachTick
            # half goes to be sold to market at valuation of treasury
            # if we have a $100 treasury and introduce 5% more tokens they should be valued at $5
            sold = (self.newTokensEachTick/2)/self.totalTokenSupply * self.total
            self.total += sold
            self.fundsRaised += sold

    def buySwap(self, buyer, underlying):
        if(self.underlyingExposed + underlying < self.total):
            self.users[buyer].paymentsAmount += (underlying * (self.premium + self.swapAddition))/self.period
            self.swapsIssued += 1
            self.underlyingExposed += underlying

    def tick(self):
        self.swapAddition = (self.total - self.underlyingExposed) / (self.total)
        self.issueTokens()
        incomeCollected = 0
        for user in self.users:
            incomeCollected += user.paymentsAmount
            self.total += user.paymentsAmount/2     #half because half tokens are on market
            user.balance -= user.paymentsAmount
        self.totalIncome += incomeCollected/2
        print("\tPeriod",self.__incrementCount())
        print("Available:\t",(self.total - self.underlyingExposed))
        print("Token Supply:\t",self.totalTokenSupply)
        print("Token Price:\t",self.total/(self.totalTokenSupply/2))
        print("Income Per Token:\t",incomeCollected / self.totalTokenSupply)
        print("Total:\t\t\t",self.total)

    def __incrementCount(self):
        self.count = self.count+1
        return self.count

users = [user(1000),user(2000),user(4000)]

t = treasury(users,1000)

#
#   Probability of purchasing bond or swap is based on APY
#
oneHundredPercent = 100
probBuySwap = 1/((t.premium + t.swapAddition) * oneHundredPercent)

xvals = []
yvals = []

xvals2 = []
yvals2 = []

totals = 0
for i in range(0,10000):
    xvals.append(i)
    xvals2.append(i)
    for j in range(0,3):

        if(random.randint(0,oneHundredPercent) < probBuySwap):
            t.buySwap(j,100)
    t.tick()
    yvals.append((t.swapsIssued))
    # yvals2.append(t.totalIncome)

print("swaps issued: ",t.swapsIssued)
print("Funds Raised: ", t.fundsRaised)
print("Total Income: ",t.totalIncome)

plt.plot(xvals,yvals)
# plt.plot(xvals2,yvals2)

plt.show()
