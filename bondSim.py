import random

"""
Stablecoin bond system
buys bonds and pays them back over a length of some periods + premium.
This works but a balance needs to be struck between the issuance of bonds and swaps
"""

#user class

class user:
    bondPayment = 0
    paymentsAmount = 0
    bondDue = 0
    def __init__(self, balance):
        self.balance = balance

# treasury is the main class
class treasury:
    count = 0                   #sim itteration
    total = 0                   #total $ in treasury
    totalBondsPrincipal = 0     #total bond principal issued
    interstDue = 0              #interest due on bonds at the moment
    premium = 0.05              #premium accrues over periods linearly across periods
    swapAddition = 0.05         #extra % (on top of bond premium) added to swaps APR
    period = 10                 #periods of bond accrual of the premium
    swapsIssued = 0             #count of swaps issued
    bondsIssued = 0             #count of bonds issued
    errors = 0                  #count of periods where there were not enough funds in treasury
    underlyingExposed = 0
    def __init__(self,users,startingPaddingTotal):
        self.total = startingPaddingTotal
        self.users = users

    def buyBond(self, buyer, cost):
        if(not self.isOverDueOnBonds(cost)):
            self.users[buyer].balance -= cost
            self.total += cost
            self.totalBondsPrincipal += cost
            self.users[buyer].bondDue += cost + cost * self.premium
            self.users[buyer].bondPayment += (cost + cost * self.premium) / self.period
            self.bondsIssued+=1

    def buySwap(self, buyer, underlying):
        if(self.underlyingExposed + underlying < self.total):
            self.users[buyer].paymentsAmount += (underlying * (self.premium + self.swapAddition))/self.period
            self.swapsIssued += 1
            self.underlyingExposed += underlying

    def isOverDueOnBonds(self,toAdd):
        return((self.interstDue + self.totalBondsPrincipal) + (toAdd + toAdd*self.premium) > self.total)

    def tick(self):
        for user in self.users:
            if(user.bondDue > 0):
                self.interstDue += user.bondPayment
                user.bondDue -= user.bondPayment

            self.total += user.paymentsAmount
            user.balance -= user.paymentsAmount

        print("\tPeriod",self.__incrementCount())
        
        print("Total:\t\t\t",self.total)
        print("Due to bond holders:\t",self.interstDue+self.totalBondsPrincipal)
        if(self.isOverDueOnBonds(0)):
            self.errors += 1
            print("X\tError not enough funds")

    def __incrementCount(self):
        self.count = self.count+1
        return self.count

users = [user(1000),user(2000),user(4000)]

t = treasury(users,1000)

#
#   Probability of purchasing bond or swap is based on APY
#
oneHundredPercent = 100
propBuyBond = t.premium * oneHundredPercent
probBuySwap = 1/((t.premium + t.swapAddition) * oneHundredPercent)

totals = 0
for i in range(0,1000):
    if(t.isOverDueOnBonds(100)):
        probBuyBond = 0
    
    for j in range(0,3):

        if(random.randint(0,oneHundredPercent) < propBuyBond):
            t.buyBond(j,100)
        elif(random.randint(0,oneHundredPercent) < probBuySwap):
            t.buySwap(j,100)
    t.tick()

print("swaps issued: ",t.swapsIssued)
print("bonds issued: ",t.bondsIssued)
print("counts with errors: ",t.errors)


