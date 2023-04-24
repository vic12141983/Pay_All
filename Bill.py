from PaymentMethod import PaymentMethod
from User import User

import datetime
class Bill:
    def __init__(self, user, payment_method, amount):
        self.user = user
        self.payment_method = payment_method
        self.amount = amount
        self.billing_accounts = []
        self.payment_history = []
        self.recurring_payments = []
        self.frequency = 30 
        # 30 days for recurring payments

    def view_bills(self):
        pass

    def setUpRecurringPayments(self, amount, billing_account, payment_method):

        frequency = self.frequency

        if payment_method is None:
            print("Error: No payment method available")
            reply = input("Would you like to add a payment method now? Y/N")
            if reply == "Y":
                name = input("Name: ")
                type = input("Type: ")
                expYear = input("Expiration Year: ")
                num = input("Card Number: ")
                code = input("Security Code: ")
                route = input("Routing: ")
                payment_method = self.payment_method.addPaymentMethod(name, type, expYear, num, code, route)

            else:
                print("Error: No Payment Method Found")
                return
            
        if billing_account not in self.billing_accounts:
            print("Error: Billing account not found")
            return 

        if amount <= 0:
            print("Error: Invalid bill amount")
            return

        recurring_payment = {
            "billing_account": billing_account,
            "payment_method": payment_method,
            "bill_amount": amount,
            "last_payment_date": datetime.now().date()
        }

        self.recurring_payments.append(recurring_payment)
        self.payment_history.append(recurring_payment)

        print(f"Recurring payment set up for billing account: {recurring_payment['billing_account']}, payment method: {recurring_payment['payment_method']}, in the amount of: {recurring_payment['bill_amount']}.")


    def linkBillingAccount(self):
        pass

    def deleteBillingAccount(self):
        pass

    def addBillingAccount(self):
        pass

    def pay_bill(self, amount, billing_account, payment_method):
        
        if amount <= 0:
            print("Error: Invalid payment amount")
            return

        if billing_account not in self.billing_accounts:
            print("Error: Billing account not found")
            return 

        if self.payment_method is None:
            print("Error: No payment method available")
            return

        payment = {
            "billing_account": billing_account,  
            "payment_method": payment_method,
            "payment_amount": amount,
            "payment_date": datetime.now().date()
        }

        self.payment_history.append(payment)

        print(f"Payment of {payment['payment_amount']} made on {payment['payment_date']} for billing account {payment['billing_account']} using payment method {payment['payment_method']}")
        reply = input("Would you like to set up recurring payments for this bill? Y/N")

        if reply == "Y":
            self.setUpRecurringPayments(amount, billing_account, payment_method)
        if reply == "N":
            return


    def viewPaymentHistory(self):
        pass


# Test
user = User("Victor", "verification", False, "Fed Now", 50.0)
bill = Bill(user, 100, "netflix")
bill.setUpRecurringPayments(100, "netflix", "visa")