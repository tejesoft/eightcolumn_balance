# -*- coding: utf-8 -*-

import time
from odoo import api, models
import sys, warnings
from dateutil.parser import parse
from odoo.exceptions import UserError

from odoo.exceptions import except_orm


class ReportEightColumns(models.AbstractModel):
    _name = 'report.eightcolumn_balance.report_eightcolumns'
    
    def _get_accounts_types(self):
        # compute the balance, debit and credit for the provided accounts
        account_result = {}
        request = "SELECT aa.id as id, afr.name as type " +\
                  "FROM public.account_account aa, public.account_account_type aat, " +\
                  "public.account_account_financial_report_type aafrt, public.account_financial_report afr " +\
                  "WHERE aat.id = aa.user_type_id AND aafrt.account_type_id = aat.id AND " +\
                  "aafrt.report_id = afr.id"
        self.env.cr.execute(request)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        return account_result

    def _compute_total(self, account_res):
        balance_total = {}
        for account_row in account_res:
            for key in account_row.keys():
                if type(account_row[key]) is float:
                    balance_total[key] = balance_total.get(key, 0) + account_row[key]

        return balance_total


    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
                `balance_pos`: total amount of deudor,
                `balance_neg`: total amount of acreedor,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        #asociarle a la cuenta la clasificación
        '''
        "Liability"
        "Income"
        "Expense"
        "Assets"                
        '''

        account_types = self._get_accounts_types()

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'balance_pos', 'balance_neg', 'Liability', 'Assets', 'Income', 'Expense',''])
            #res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'balance_pos', 'balance_neg', 'Liability', 'Assets', 'Income', 'Expense','Receivable', 'Payable', 'Bank and Cash', 'Credit Card', 'Current Assets', 'Non-current Assets', 'Prepayments', 'Fixed Assets', 'Current Liabilities', 'Non-current Liabilities', 'Equity', 'Current Year Earnings', 'Other Income', 'Depreciation', 'Cost of Revenue', 'Cuentas No Clasificadas',''])

            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name

            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')


            #try:

                account_type = str(account_types.get(account.id).get('type'))

            #except AttributeError:
             #   raise except_orm('Debe configurar los tipos de cuentas y configurar los informes financieros')



                res[account_type] = res['balance']  #'Liability', 'Assets', 'Income', 'Expense'
                if res['balance'] > 0 :
                    res['balance_pos'] = res['balance']
                else:
                    res['balance_neg'] = abs(res['balance'])
            if display_account == 'all':
                account_res.append(res)
            if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
            'Totals': self._compute_total(account_res)
        }
        return self.env['report'].render('eightcolumn_balance.report_eightcolumns', docargs)
