#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 11:50:01 2023

@author: buzz66boy
"""

from collections import deque
# import sys

#local imports
import PaymentMethod
import Bill

class CLISession:
    def __init__(self, cli, sessID, rootSess = False, user = None, billingAcct = None, histLen = 10):
        self.__sessionID = sessID
        self.cli = cli
        self.rootSess = rootSess
        self.user = user
        self.billingAcct = billingAcct
        
        self.history = deque(maxlen = histLen) #user accessible to see previous commands
        self.internalHistory = deque(maxlen = 100) #this is for debugging purposes
        
        #Syntax Map dict(key=ScreenName, val=dict(key = function names, val = list([args & description, function pointer])))
        self.syn_map = dict()
        
        #map non-common homescreen commands
        self.syn_map[cli.homeScreenName] = dict()
        self.syn_map[cli.homeScreenName][cli.kwLogin] = ["usage: '" + cli.kwLogin + " username password', logs into the specified user's account", self.login]
        self.syn_map[cli.homeScreenName][cli.kwCreateAcct] = ["usage '" + cli.kwCreateAcct + " username password' creates a new account with username specified if one doesn't exist", self.createAccount] #FIXME: Add function
        
        #self.syn_map[cli.adminScreenName] = dict()
        
        self.syn_map[cli.userHomeScreenName] = dict()
        self.syn_map[cli.userHomeScreenName][cli.kwUserSummary] = ["Show user details", self.showUser] #FIXME: need User to_string()
        self.syn_map[cli.userHomeScreenName][cli.kwDelAcct] = ["usage '" + cli.kwDelAcct + "' deletes the currently logged in account", self.deleteAccount]
        self.syn_map[cli.userHomeScreenName][cli.kwModAcct] = ["Usage 'modacct username value' or 'modacct changepassword value'", self.modAccount]
        
        self.syn_map[cli.userHomeScreenName][cli.kwAddPaymentMethod] = ["Add payment method with name '" + cli.kwAddPaymentMethod + " method_name', takes you to prompts for input", self.addPaymentMethod]
        self.syn_map[cli.userHomeScreenName][cli.kwPaymentMethodList] = ["Show user details", self.showUser]
        self.syn_map[cli.userHomeScreenName][cli.kwRemovePaymentMethod] = ["Usage '" + cli.kwRemovePaymentMethod + " method_name'. Remove payment method", self.rmPaymentMethod]
        
        self.syn_map[cli.userHomeScreenName][cli.kwAddBillingAccount] = ["Usage '" + cli.kwAddBillingAccount + " acct_name' adds a new billing account", self.addBillingAcct]
        self.syn_map[cli.userHomeScreenName][cli.kwNavBillingAccount] = ["", self.showBillingAcct]
        self.syn_map[cli.userHomeScreenName][cli.kwRmBillingAccount] = ["", self.rmBillingAcct]
        self.syn_map[cli.userHomeScreenName][cli.kwListBillingAccount] = ["", self.showUser]
        
        self.syn_map[cli.userHomeScreenName][cli.kwShowUnpaidBills] = ["", self.showUnpaidBills]
        self.syn_map[cli.userHomeScreenName][cli.kwShowAllBills] = ["", self.showAllBills]
        self.syn_map[cli.userHomeScreenName][cli.kwQueryNewBills] = ["", self.queryNewBills]
        self.syn_map[cli.userHomeScreenName][cli.kwPayBill] = ["", self.payBill]
        
        # kwAddBillingAccount = "addbillingacct"
        # kwNavBillingAccount = "showbillingacct"
        # kwRmBillingAccount = "rmbillingacct"
        # kwListBillingAccount = "listbillingacct"
        
        # #For both userhome and specific to a billing account
        # kwShowUnpaidBills = "showbills"
        # kwShowOldBills = "showpaidbills"
        # kwQueryNewBills = "syncbills"
        # paybill
        
        # #BillingAcct view specific
        # kwNavHome = "userhome" #exits the view of a specific billing acct
        
        self.syn_map[cli.billAcctViewScreenName] = dict()
        self.syn_map[cli.billAcctViewScreenName][cli.kwShowUnpaidBills] = ["", self.showUnpaidBills]
        self.syn_map[cli.billAcctViewScreenName][cli.kwShowAllBills] = ["", self.showAllBills]
        self.syn_map[cli.billAcctViewScreenName][cli.kwQueryNewBills] = ["", self.queryNewBills]
        self.syn_map[cli.billAcctViewScreenName][cli.kwPayBill] = ["", self.payBill]
        
        self.syn_map[cli.billAcctViewScreenName][cli.kwNavHome] = ["Navigates system back to user home screen (out of billing account)", self.navHome]
        
        #help, history, and logout population on all screens
        for keyScrn in self.syn_map:
            self.syn_map[keyScrn][cli.kwHelp] = [cli.helpMsg, self.__help]
            self.syn_map[keyScrn][cli.kwHist] = ["usage '" + cli.kwHist + "' displays last 10 commands", self.__hist]
            self.syn_map[keyScrn][cli.kwExit] = ["Exits the program", None] #Special case #FIXME: add logout and exit methods
            if keyScrn != cli.homeScreenName:
                self.syn_map[keyScrn][cli.kwLogout] = [cli.logoutMsg, self.logout] #FIXME: Add function
        
        if user == None:
            self.curScreen = cli.homeScreenName
        else:
            self.curScreen = cli.userHomeScreenName
            if user.administrator != None and user.administrator:
                self.__adminCmds(user.administrator)
        
    def __sanitize(self, string):
        return string.lower()

    def __help(self):
        helpStr = ""
        for key in self.syn_map[self.curScreen]:
            helpStr +=  key + " -- " + self.syn_map[self.curScreen][key][0] + "\n"
           
        self.display(helpStr)
        
    def __hist(self):
        histStr = ""
        for i in range(len(self.history)):
            histStr += str(len(self.history) - i) + ": " + self.history[i] + "\n"
        self.display(histStr)
    
    def __adminCmds(self, add = False):
        if add:
            # change delete account behavior to be able to delete any account
            #self.syn_map[self.userHomeScreenName][cli.kwDelAcct]
            self.syn_map[self.cli.userHomeScreenName][self.cli.kwUsrList] = ["list the User accounts of the system", self.listUsers]
            self.syn_map[self.cli.userHomeScreenName][self.cli.kwOtherUsrSummary] = ["Usage: '" + self.cli.kwOtherUsrSummary + " username' shows the details of the specified user", self.showUser]
        else:
            self.syn_map[self.cli.userHomeScreenName].pop(self.cli.kwUsrList, None)
            self.syn_map[self.cli.userHomeScreenName].pop(self.cli.kwOtherUsrSummary, None)
    
    def listUsers(self):
        self.display(str(self.cli.users.keys()))
    
    def showUser(self, usr = None):
        if usr == None:
            usr = self.user.username
        print(str(self.cli.users[usr]))
    
    def getSessionID(self):
        return self.__sessionID
    
    def display(self, string):
        print(string)
        #FIXME: add to log file
    
    def login(self, user, password):
        #FIXME multiprocess query for user
        success, usr = self.cli.login(user, password)
        if success:
            self.user = usr
            self.curScreen = self.cli.userHomeScreenName
            self.display(self.cli.loginOkMsg)
            #admin
            #if self.user != None and self.user.isAdmin(): #FIXME
            if usr.administrator != None and usr.administrator: #FIXME hardcoded admin
                #populate admin commands
                self.__adminCmds(usr.administrator)
        else:
            self.display(self.cli.loginBadMsg)
            
    def createAccount(self, user, password):
        success, usr = self.cli.createAccount(user, password)
        if success:
            self.display(self.cli.acctCreateOkMsg)
            self.login(user, password)
        else:
            self.display(self.cli.acctExistsMsg)
    
    def logout(self):
        self.curScreen = self.cli.homeScreenName
        if self.user.administrator != None and self.user.administrator:
            self.__adminCmds()
        self.user = None
        #FIXME: depopulate admin commands
    
    def deleteAccount(self, usrName = None):
        if usrName == None:
            usrName = self.user.username
        self.cli.deleteAccount(usrName)
        self.logout()
        
    def modAccount(self, keyword, value):
        if keyword == self.cli.kwModAcctUsername:
            if self.cli.renameAccount(self.user, value):
                self.user.modify_account(username = value)
            else:
                #username taken
                self.display(self.cli.acctExistsMsg)
        elif keyword == self.cli.kwModAcctPassword:
            self.user.modify_account(password = value)
        else:
            #unrecognized keyword
            self.display("Unrecognized Account Modification keyword, try ")

    def addPaymentMethod(self, method_name):
        if not PaymentMethod.valName(self.user, method_name):
            return
        
        can = 'cancel'
        self.display("enter '" + can + "' at any prompt to cancel")
        
        typ = self.getUserInput("Enter type (Debit or Credit)")
        while typ != can and not PaymentMethod.valType(typ):
            typ = self.getUserInput("Enter type (Debit or Credit)")
        
        if typ == can:
            self.display("Cancelled")
            return
        
        #expiration
        exp = self.getUserInput("Enter expiration year")
        while exp != can and not PaymentMethod.valExp(exp):
            exp = self.getUserInput("Enter expiration year")
            
        if exp == can:
            self.display("Cancelled")
            return
            
        #number
        num = self.getUserInput("Enter card number (16 digits)")
        while num != can and not PaymentMethod.valNum(num):
            num = self.getUserInput("Enter card number")
        
        if num == can:
            self.display("Cancelled")
            return
        
        #sec code
        cvv = self.getUserInput("Enter card security code (3 digits)")
        while cvv != can and not PaymentMethod.valSecCode(cvv):
            cvv = self.getUserInput("Enter card security code")
        
        if cvv == can:
            self.display("Cancelled")
            return
        
        #routing number
        rout = self.getUserInput("Enter card routing number (9 digits)")
        while rout != can and not PaymentMethod.valRouteNum(rout):
            rout = self.getUserInput("Enter card security code")
        
        if rout == can:
            self.display("Cancelled")
            return
        
        PaymentMethod.addPaymentMethod(self.user, method_name, typ, exp, num, cvv, rout)
        
        
    def rmPaymentMethod(self, method_name):
        PaymentMethod.deletePaymentMethod(self.user, method_name)
    
    def addBillingAcct(self, acct_name):
        self.display(Bill.addBillingAccount(self.user, acct_name))
    
    def rmBillingAcct(self, acct_name):
        self.display(Bill.deleteBillingAccount(self.user, acct_name))
    
    def showBillingAcct(self, acct_name):
        if(acct_name not in self.user.billing_accounts):
            self.display("Billing account of that name does not exist")
            return
        self.billingAcct = acct_name
        self.curScreen = self.cli.billAcctViewScreenName
        self.display("Showing Billing Account\n" + str(self.user.billing_accounts[acct_name]))
        
    def showUnpaidBills(self):
        bills = []
        if self.curScreen == self.cli.billAcctViewScreenName and self.billingAcct != None and self.billingAcct in self.user.billing_accounts:
            bills = self.user.billing_accounts[self.billingAcct].getBills(paid = False)
            self.display("Unpaid Bills from Billing Account: {}".format(self.billingAcct))
        elif self.billingAcct != None: #billing account missing from user! error
            pass
        else: #not on specific billing account, show all unpaid bills
            for billAcct in self.user.billing_accounts.values():
                bills = bills + billAcct.getBills(paid = False)
            self.display("All unpaid bills:")
            
        for bill in bills:
            self.display("\n\t" + str(bill))
            
    
    def showAllBills(self):
        bills = []
        if self.curScreen == self.cli.billAcctViewScreenName and self.billingAcct != None and self.billingAcct in self.user.billing_accounts:
            bills = self.user.billing_accounts[self.billingAcct].getBills(paid = True)
            self.display("Bills from Billing Account: {}".format(self.billingAcct))
        elif self.billingAcct != None: #billing account missing from user! error
            pass
        else: #not on specific billing account, show all unpaid bills
            for billAcct in self.user.billing_accounts.values():
                bills = bills + billAcct.getBills(paid = True)
            self.display("All bills:")
            
        for bill in bills:
            self.display("\n\t" + str(bill))
    
    def queryNewBills(self):
        rstr = ""
        if self.curScreen == self.cli.billAcctViewScreenName and self.billingAcct != None and self.billingAcct in self.user.billing_accounts:
            rstr = self.user.billing_accounts[self.billingAcct].queryBills(self.user)
        elif self.billingAcct != None: #billing account missing from user! error
            pass
        else: #not on specific billing account, show all unpaid bills
            for billAcct in self.user.billing_accounts.values():
                rstr += billAcct.queryBills(self.user) + '\n'
                
        self.display(rstr)
    
    def payBill(self):
        bill = None
        billList = []
        if self.curScreen == self.cli.billAcctViewScreenName and self.billingAcct != None and self.billingAcct in self.user.billing_accounts:
            if len(self.user.billing_accounts[self.billingAcct].bills) < 1:
                #no bills to pay
                self.display("No bills associated with billing account")
                return
            elif len(self.user.billing_accounts[self.billingAcct].getBills(paid = False)) == 1: #only one bill to pay
                bill = self.user.billing_accounts[self.billingAcct].getBills(paid = False)[0]
            else:
                #bill selection
                billList = self.user.billing_accounts[self.billingAcct].getBills(paid = False)
        else: #not on specific billing acct, list all bills
            for billAcct in self.user.billing_accounts.values():
                billList = billList + billAcct.getBills(paid = False)
                
        #selection in case multiple bills
        if bill is None and len(billList) < 1:
            self.display("No bills to pay")
            return
        elif len(billList) == 1:
            bill = billList[0]
        elif bill is None:
            i = 0
            for billselect in billList:
                self.display("Bill " + str(i + 1) + ": " + str(billselect))
                i += 1
            self.display("Type 'cancel' to cancel paying the bill")
            inp = "0"
            while (not inp.isnumeric() and inp.lower() != "cancel") or (inp.isnumeric() and int(inp) not in range(1, i + 1)):
                inp = self.getUserInput("Select a bill (1-" + str(i) + ")")
            if inp == "cancel":
                self.display("Cancelled paying bill")
                return
            bill = billList[int(inp) - 1]
            
        self.display("Paying Bill: " + str(bill))
        
        #get payment method
        method = None
        if len(self.user.payment_methods) < 1:
            #error
            self.display("No payment methods, please add one before paying a bill")
            return
        elif len(self.user.payment_methods) == 1:
            method = list(self.user.payment_methods.values())[0]
        else:
            #select payment method
            self.display("Type 'cancel' to cancel paying the bill")
            while inp not in self.user.payment_methods and inp != 'cancel':
                self.display("Select payment method by name, options: " + str(self.user.payment_methods.keys()))
                inp = self.getUserInput()
            if inp == "cancel":
                self.display("Cancelled paying bill")
                return
            method = self.user.payment_methods[inp]
            
        #select amount to pay
        amt = ""
        self.display("Type 'cancel' to cancel paying the bill")
        while amt != 'cancel':
            amt = self.getUserInput("Enter amount to pay in range (0.01 - " + str(bill.unpaid_amount) + ") - $")
            try:
                if float(amt) <= 0 or float(amt) > bill.unpaid_amount:
                    self.display("Invalid amount " + amt)
                else:
                    break
            except (ValueError, TypeError):
                if amt != 'cancel':
                    self.display("Amount could not be interpreted as a number, use the format '0.00'")
        if amt == 'cancel':
            self.display("Cancelled paying bill")
            return
            
        bill.pay_bill(float(amt), method)
        
        self.display("Bill paid: " + amt + "from method:" + method.name)
        self.display(str(bill))
    
    def navHome(self):
        self.curScreen = self.cli.userHomeScreenName
        self.billingAcct = None
    
    # kwAddBillingAccount = "addbillingacct"
    # kwNavBillingAccount = "showbillingacct"
    # kwRmBillingAccount = "rmbillingacct"
    # kwListBillingAccount = "listbillingacct"
    
    # #For both userhome and specific to a billing account
    # kwShowUnpaidBills = "showbills"
    # kwShowOldBills = "showpaidbills"
    # kwQueryNewBills = "syncbills"
    # paybill
    
    # #BillingAcct view specific
    # kwNavHome = "userhome" #exits the view of a specific billing acct
    
    def getUserInput(self, prompt = ""):
        return input(prompt + self.cli.prompt)
    
    def sessionLoop(self):
        kw = ""
        self.display(self.cli.welcomeMsg)
        while kw != self.cli.kwExit:
            inp = input(self.curScreen + self.cli.prompt)
            self.history.append(inp)
            self.internalHistory.append(inp)
            self.display(inp)
            cmd = inp.split()
            if len(cmd) > 0:
                kw = self.__sanitize(cmd[0])
                if len(cmd) > 1:
                    args = cmd[1:]
                else:
                    args = []
                if kw in self.syn_map[self.curScreen]:
                    if self.syn_map[self.curScreen][kw][1] != None: #check for keyword associated function
                        try: #except arg issues and notify user
                            self.display("Executing '" + kw + "' with args " + str(args))
                            self.syn_map[self.curScreen][kw][1](*args)
                        except TypeError as e:
                            self.display("Args error")
                            self.display(e)
                else:
                    self.display("'" + kw + "'" + self.cli.unrecCmdMsg)