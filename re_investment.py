#### RE Investments ####

import pandas as pd
from statistics import mean
from math import floor

class mortgage:
    
    def __init__(self, loan_amnt, interest, term, down_pmt):
        self.loan_amnt = loan_amnt
        self.interest = interest
        self.term = int(term) 
        self.down_pmt = down_pmt
        self.extra_pmts = dict()
        self.amort = self.amortize()
    
    def __repr__(self):
        return str(dict({"Loan Amount" : self.loan_amnt,
                     "Interest Rate" : self.interest,
                     "Term" : self.term,
                     "Down Payment" : self.down_pmt}))
    
    def summary(self):
        print('Original Balance:         ${:>11}'.format(self.loan_amnt))
        print('Interest Rate:             {:>11}%'.format(self.interest))
        print('Term:                      {:>6} Years'.format(self.term))
        print('Monthly Payment:          ${:>11}'.format(self.mthly_pmt))
        print('')
        print('Total principal payments: ${:>11}'.format(self.total_principle_paid))
        print('Total interest payments:  ${:>11}'.format(self.total_interest_paid))
        print('Total extra payments:     ${:>11}'.format(-self.total_extra_pmts))
        print('Total payments:           {:>11}'.format(len(self.amort)))
        print('Loan Payoff Year:         {:>11}'.format(round(len(self.amort)/12), 2))
        print('Interest to principal:     {:>11}%'.format(self.interest_to_principle))
    
    def amortize(self):
        bop = [self.loan_amnt]
        interest = []
        principle = []
        pmt = []
        eop = []
        mnth = []
        extra = []
        mthly_term = int(self.term) *12
        mthly_int = (1+self.interest)**(float(1)/12)-1
        mthly_pmt = self.loan_amnt/((1-(1+mthly_int)**(-mthly_term))/(mthly_int))
        self.mthly_pmt = round(mthly_pmt, 2)
        self.mthly_term = mthly_term
        
        i = 0
        
        while bop[i]>0:
            mnth.append(i)
            interest.append(bop[i]*(mthly_int))
            principle.append(-mthly_pmt+interest[i]) 
            pmt.append(-mthly_pmt)
            if self.extra_pmts.get(i)!=None:
                extra.append(self.extra_pmts[i])
            else:
                extra.append(0)
            eop.append(bop[i]+interest[i]+pmt[i]+extra[i])
            if eop[i]>0:
                bop.append(eop[i])
            else:
                break
            i += 1
        
        df = pd.DataFrame({"Month" : mnth, "BOP" : bop, "Interest" : interest,
                            "Principle" : principle, "PMT" : pmt, "Extra PMT" : extra, "EOP" : eop})
        self.interest = interest
        self.total_interest_paid = round(sum(df['Interest']), 2)
        self.total_principle_paid = -round(sum(df['Principle']), 2)
        self.total_extra_pmts = round(sum(df['Extra PMT']), 2)
        self.interest_to_principle = round(self.total_interest_paid/float(self.loan_amnt), 2)*100
            
        return df
    
    def add_pmt(self, month, amnt, length=0):
        current_pmts = self.extra_pmts
        if length:
            for i in range(0, length):
                self.extra_pmts[month+i] = amnt
        self.amort = self.amortize()
        if len(self.amort)<month:
            self.extra_pmts = current_pmts
            return "Loan is already paid off."
        else:
            print("Added $%s to mortgage payment in month %s." % (str(amnt), str(month))) 


class revenue:
    
    def __init__(self, years, rent, increase, start, occupancy):
        self.years = int(years)
        self.rent = dict()
        self.rent[0] = rent
        self.increase = increase
        self.start = start
        self.occupancy = occupancy
        self._calculate()
    
    def _occupancy_sim(self):
        from scipy.stats import poisson
        
        #Empty list for rent sim.
        output = []
        
        #Simulation
        if self.occupancy['type'] == "simulation":
            for i in range(0, self.start):
                output.append(0)
            while len(output) < self.years * 12:
                for i in range(0, poisson.rvs(self.occupancy['values'][1])):
                    output.append(0)
                for i in range(0, poisson.rvs(self.occupancy['values'][0])):
                    output.append(1)
        else:
            for i in range(0, self.start):
                output.append(0)
            while len(output) < self.years * 12:
                output.append(1-self.occupancy['values'][0])
        
        self.occupancy_sim = output
    
    def _rent_sim(self):
        
        #Function to get rent for when manual changes.        
        def get_rent(month, rent_dict):
            rent_months = list(rent_dict.keys())
            rent_months = [i for i in rent_months if i <= month]
            return rent_dict[max(rent_months)]
        
        output = []
        base_rent = []
        
        rent_months = 1
        for i in range(0, self.years * 12):
            rent = get_rent(i, self.rent)
            base_rent.append(rent)
            if base_rent[i-1] != base_rent[i]:
                rent_months = 1
                rent = base_rent[i]
            else:
                rent = base_rent[i-1]
                rent_months += 1
                
            output.append(round(rent*((1+self.increase)**(floor((rent_months/12)))), 2))
            
        self.rent_sim = output
        
    def _revenue_sim(self):
        self.scheduled_gross = self.rent_sim
        self.vacancy_loss = [i*(j-1) for i,j in zip(self.scheduled_gross, self.occupancy_sim)]
        self.effective_gross = [i+j for i,j in zip(self.scheduled_gross, self.vacancy_loss)] 
        
    def change_rent(self, month, rent):
        self.rent[month] = rent
        self._calculate()
        
    def _calculate(self):
        self._occupancy_sim()
        self._rent_sim()
        self._revenue_sim()
    
class expenses:
    
    def __init__(self, years, home_value, property_tax, property_management, utilities, opex_growth):
        self.home_value = home_value
        self.years = years
        self.tax_rate = property_tax
        self.management_fee = property_management
        self.mthly_utilities = utilities
        self.opex_growth_rate = opex_growth
        self._expense_sim()
    
    def _expense_sim(self):
        #All the expense assumptions.
        from math import floor
        
        taxes = []
        fees = []
        utilities = []
        total_opex = []
        
        for i in range(0, int(self.years)*12):
            taxes.append(-self.home_value*((1+self.tax_rate)**(1/12)-1)*(1+self.opex_growth_rate)**(floor(i/24)))
            fees.append(self.management_fee*(1+self.opex_growth_rate)**(floor(i/12)))
            utilities.append(self.mthly_utilities*(1+self.opex_growth_rate)**(floor(i/12)))
            total_opex.append(round(taxes[i] + fees[i] + utilities[i], 2))
        
        self.taxes = taxes
        self.fees = fees
        self.utilities = utilities
        self.total_opex = total_opex

class capex:
    
    def __init__(self):
        self.capex = dict()
        
    def add_capex(self, month, cost):
        self.capex[month] = cost
   
class returns:
    
    def __init__(self, mortgage_sim, revenue_sim, expenses_sim, capex_sim):
        self.mortgage_sim = mortgage_sim
        self.revenue_sim = revenue_sim
        self.expenses_sim = expenses_sim
        self.capex_sim = capex_sim
        self.discount_rate = .10
        self._calculate()
    
    def _calculate(self):
        self._cash_flow_sim()
        self._metrics_sim()
        
    
    def _cash_flow_sim(self):
        #Net Operating Income
        self.net_operating_income = [round(i+j, 2) for i,j in zip(self.revenue_sim.effective_gross, self.expenses_sim.total_opex)]
        
        #Monthly Cash Flow
        self.cash_flow = [round(i-j, 2) for i,j in zip(self.net_operating_income, [self.mortgage_sim.mthly_pmt]*len(self.net_operating_income))]
        self.months = [i for i in range(0, len(self.net_operating_income))]
        
        #Initial Outaly
        self.cash_flow[0] -= self.mortgage_sim.down_pmt
        #Extra Mortgage Payments
        for i in self.mortgage_sim.extra_pmts.keys():
            self.cash_flow[i] += self.mortgage.extra_pmts[i]
        
        #Additional Capex
        self.capex = [0] * int(self.revenue_sim.years) * 12
        for i in self.capex_sim.capex.keys():
            self.capex[i] += self.capex_sim.capex[i]
            self.cash_flow[i] += self.capex[i]
            
        self.cum_cash_flow = [sum(self.cash_flow[:i]) for i in range(0, len(self.cash_flow))]
            
    def _metrics_sim(self):
        from numpy import npv, irr
        self.cap_rate = [i/self.expenses_sim.home_value for i in self.net_operating_income]
        self.cash_on_cash = []
        
        capex = 0
        cum_capex = []
        invested_cap = []
        initial_outlay = self.mortgage_sim.down_pmt
        
        for i in range(0, self.revenue_sim.years * 12):
            if self.capex_sim.capex.get(i) != None:
                capex += self.capex_sim.capex[i]
            cum_capex.append(capex)
            invested_cap.append(sum([-initial_outlay, cum_capex[i]]))
                
            self.cash_on_cash.append(-self.cash_flow[i]/invested_cap[i])
        self.invested_capital = invested_cap
        self.av_cash_on_cash = round(mean(self.cash_on_cash) * 12, 4)
        self.av_cap_rate = round(mean(self.cap_rate) * 12, 4)
        self.npv = round(npv((1+self.discount_rate)**(1/12)-1, self.cash_flow), 2)
        self.irr = round(irr(self.cash_flow) * 12, 4)
        
    def summary(self):
        self._calculate()
        df = pd.DataFrame({"Month" : self.months, 
                           "Scheduled Gross" : self.revenue_sim.scheduled_gross,
                           "Vacancy Loss" : self.revenue_sim.vacancy_loss,
                           "Effective Gross" : self.revenue_sim.effective_gross,
                           "Taxes" : self.expenses_sim.taxes,
                           "Fees" : self.expenses_sim.fees,
                           "Utilities" : self.expenses_sim.utilities,
                           "Total Opex" : self.expenses_sim.total_opex,
                           "Net Operating Income" : self.net_operating_income,
                           "CAPEX" : self.capex,
                           "Mortgage Expense" : [-self.mortgage_sim.mthly_pmt]*len(self.net_operating_income), 
                           "Net Cash Flow" : self.cash_flow,
                           "Cumulative Net Cash Flow" : self.cum_cash_flow,
                           "Total Invested Capital" : self.invested_capital,
                           "Cap Rate" : self.cap_rate,
                           "Cash on Cash" : self.cash_on_cash})
        return df
    
    def graph(self, x, y):
        import seaborn as sns
        import matplotlib.pyplot as plt
        
        data=pd.DataFrame({"x" : x, "y" : y})
        
        ax = sns.lineplot(x="x", y="y", data=data, estimator=None)
        return(ax)


class mc:
    
    def __init__(self, reps, mortgage_parms, revenue_parms, 
                 expense_parms, capex_parms):
        self.reps = reps
        self.mortgage_parms = dict(mortgage_parms)
        self.revenue_parms = dict(revenue_parms)
        self.expense_parms = dict(expense_parms)
        self.capex_parms = dict(capex_parms)
        self._mortgage_parms()
        self._revenue_parms()
        self._expense_parms()
        self.sim = self._sim()
        
    def get_sim(self, parm):
        from scipy.stats import poisson, uniform, norm
        
        try:
            distribution = parm["distribution"]
            value = parm["value"]
        
            if distribution=="uniform":
                output = uniform.rvs(value[0], value[1], size=self.reps)
            elif distribution=="poisson":
                output = poisson.rvs(value[0], size=self.reps)
            elif distribution=="normal":
                output = norm.rvs(value[0], value[1], size=self.reps)
                
        except:
            value = parm
            output = [value] * self.reps
            
        return output
            
    def _mortgage_parms(self):
        self.years = self.get_sim(self.mortgage_parms["term"])
        self.loan_amnt = self.get_sim(self.mortgage_parms["loan_amnt"])
        self.interest = self.get_sim(self.mortgage_parms["interest"])
        self.down_pmt = self.get_sim(self.mortgage_parms["down_pmt"])
        
    
    def _revenue_parms(self):
        self.rent_mult = self.get_sim(self.revenue_parms["rent_mult"])
        self.increase = self.get_sim(self.revenue_parms["increase"])
        self.start = self.get_sim(self.revenue_parms["start"])
        self.occupancy = self.get_sim(self.revenue_parms["occupancy"])
        self.new_rent = self.get_sim(self.revenue_parms["change_rent"])
        
    def _expense_parms(self):
        self.property_tax = self.get_sim(self.expense_parms["property_tax"])
        self.property_management = self.get_sim(self.expense_parms["property_management"])
        self.utilities = self.get_sim(self.expense_parms["utilities"])
        self.opex_growth = self.get_sim(self.expense_parms["opex_growth"])
        
    def _sim(self):
        output = []
        
        for i in range(0, self.reps):
            print(i)
            #Mortgage
            mortgage_sim = mortgage(loan_amnt=self.loan_amnt[i], interest=self.interest[i], 
                                term=self.years[i], down_pmt=self.down_pmt[i])
    
            #Revenue
            revenue_sim = revenue(years=self.years[i], rent=self.loan_amnt[i]*self.rent_mult[i], 
                              increase=self.increase[i], start=self.start[i], occupancy=self.occupancy[i])
            
            #Expenses
            expenses_sim = expenses(years=self.years[i], home_value=self.loan_amnt[i], 
                                property_tax=self.property_tax[i], 
                                property_management=self.property_management[i], 
                                utilities=self.utilities[i], opex_growth=self.opex_growth[i])
            capex_sim = capex()
            for j in range(0, len(self.capex_parms["months"])):
                capex_sim.add_capex(self.capex_parms["months"][j], self.capex_parms["costs"][j])
                
            revenue_sim.change_rent(self.new_rent[i][0], self.new_rent[i][1])
            returns_sim = returns(mortgage_sim, revenue_sim, expenses_sim, capex_sim)
            returns_sim.discount_rate = .06
            output.append(returns_sim)
            
        return output
                    
'''
mortgage_parms = {"loan_amnt" : 200000,
                  "interest" : .03,
                  "term" : 30,
                  "down_pmt" : 15000,
                  }

occupancy = {'type' : "simulation", #distribution = ["poisson"]
             'distribution' : "poisson", 
             'values' : [12, 3] #Poisson=[occupancy_length, vacancy_length]
             }

revenue_parms = {"rent_mult" : {"distribution" : "uniform", "value" : [.005, .0075]},
                "rent_amnt" : None, 
                 "increase" : {"distribution" : "uniform", "value" : [0, .02]},
                 "start" : {"distribution" : "poisson", "value" : [6]},
                 "occupancy" : occupancy,
                 "change_rent" : [24, 1800]
                  }

expense_parms = {"property_tax" : {"distribution" : "uniform", "value" : [.0219, .03]},
                  "property_management" : {"distribution" : "uniform", "value" : [100, 200]},
                  "utilities" : {"distribution" : "normal", "value" : [300, 50]},
                  "opex_growth" : {"distribution" : "uniform", "value" : [0, .02]}
                  }

capex_parms = {"months" : [4, 5, 6],
               "costs" : [-12000, -5000, -6000]}
'''

        