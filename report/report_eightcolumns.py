# -*- coding: utf-8 -*-

import time
from odoo import api, models
import sys, warnings
from dateutil.parser import parse
from odoo.exceptions import UserError, Warning

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

    def _compute_total(self, account_res,enable_negative_values):
        balance_total = {}
        for account_row in account_res:
            for key in account_row.keys():
                if type(account_row[key]) is float:
                    balance_total[key] = balance_total.get(key, 0) + account_row[key]
        if enable_negative_values:
            result ={
                'Assets': max(balance_total.get('Assets',0) - balance_total.get('Liability',0),0),
                'Liability': max(balance_total.get('Liability',0) - balance_total.get('Assets',0),0),
                'Expense': max(balance_total.get('Expense',0) - balance_total.get('Income',0),0),
                'Income': max(balance_total.get('Income',0) - balance_total.get('Expense',0),0)
            }
        else:
            result = {
                'Assets': max(balance_total.get('Assets', 0) + balance_total.get('Liability', 0), 0),
                'Liability': min(balance_total.get('Liability', 0) + balance_total.get('Assets', 0), 0),
                'Expense': max(balance_total.get('Expense', 0) + balance_total.get('Income', 0), 0),
                'Income': min(balance_total.get('Income', 0) + balance_total.get('Expense', 0), 0)
            }
        return balance_total, result

    """def _diferencia_pasivo_activo(self, account_res):
        resultado_pasivo_activo = 0.0
        key_Activo = 'Assets'
        key_Pasivo = 'Liability'
        key_AR =''
        valor_Activo = 0.0
        valor_Pasivo = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Pasivo == key_AR:
                    valor_Pasivo = valor_Pasivo + value;

                if key_Activo == key_AR:
                    valor_Activo =  valor_Activo + value;

        if valor_Pasivo > valor_Activo:
            resultado_pasivo_activo = valor_Pasivo - abs(valor_Activo);
        else:
            resultado_pasivo_activo = 0.0

        return resultado_pasivo_activo

    def _diferencia_activo_pasivo(self, account_res):
        resultado_pasivo_activo = 0.0
        key_Activo = 'Assets'
        key_Pasivo = 'Liability'
        key_AR = ''
        valor_Activo = 0.0
        valor_Pasivo = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Pasivo == key_AR:
                    valor_Pasivo = valor_Pasivo + value;

                if key_Activo == key_AR:
                    valor_Activo = valor_Activo + value;

        if valor_Activo > valor_Pasivo:
            resultado_activo_pasivo = valor_Activo - abs(valor_Pasivo);
        else:
            resultado_activo_pasivo = 0.0

        return resultado_activo_pasivo

    def _diferencia_ingresos_gastos(self, account_res):
        resultado_ingresos_gastos = 0.0
        key_Ingresos = 'Income'
        key_Gastos = 'Expense'
        key_AR = ''
        valor_Ingresos = 0.0
        valor_Gastos = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Ingresos == key_AR:
                    valor_Ingresos = valor_Ingresos + value;

                if key_Gastos == key_AR:
                    valor_Gastos = valor_Gastos + value;

        if valor_Ingresos > valor_Gastos:
            resultado_ingresos_gastos = valor_Ingresos - abs(valor_Gastos);
        else:
            resultado_ingresos_gastos = 0.0

        return resultado_ingresos_gastos

    def _diferencia_gastos_ingresos(self, account_res):
        resultado_gastos_ingresos = 0.0
        key_Ingresos = 'Income'
        key_Gastos = 'Expense'
        key_AR = ''
        valor_Ingresos = 0.0
        valor_Gastos = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Ingresos == key_AR:
                    valor_Ingresos = valor_Ingresos + value;

                if key_Gastos == key_AR:
                    valor_Gastos = valor_Gastos + value;

        if valor_Gastos > valor_Ingresos:
            resultado_gastos_ingresos = valor_Gastos - abs(valor_Ingresos);
        else:
            resultado_gastos_ingresos = 0.0

        return resultado_gastos_ingresos

    def _Total_pasivo(self, account_res):
        resultado_pasivo_activo = 0.0
        key_Activo = 'Assets'
        key_Pasivo = 'Liability'
        key_AR =''
        valor_Activo = 0.0
        valor_Pasivo = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Pasivo == key_AR:
                    valor_Pasivo = valor_Pasivo + value;

                if key_Activo == key_AR:
                    valor_Activo =  valor_Activo + value;

        if valor_Pasivo > valor_Activo:
            resultado_pasivo_activo = valor_Pasivo - abs(valor_Activo);
        else:
            resultado_pasivo_activo = 0.0

        if valor_Pasivo == resultado_pasivo_activo:
            resultado_pasivo_activo = resultado_pasivo_activo;
        else:
            resultado_pasivo_activo = valor_Pasivo + resultado_pasivo_activo;

        return resultado_pasivo_activo

    def _Total_activo(self, account_res):
        resultado_pasivo_activo = 0.0
        key_Activo = 'Assets'
        key_Pasivo = 'Liability'
        key_AR = ''
        valor_Activo = 0.0
        valor_Pasivo = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Pasivo == key_AR:
                    valor_Pasivo = valor_Pasivo + value;

                if key_Activo == key_AR:
                    valor_Activo = valor_Activo + value;

        if valor_Activo > valor_Pasivo:
            resultado_activo_pasivo = valor_Activo - abs(valor_Pasivo);
        else:
            resultado_activo_pasivo = 0.0

        if valor_Activo == resultado_pasivo_activo:
            resultado_activo_pasivo = resultado_activo_pasivo;
        else:
            resultado_activo_pasivo = valor_Activo + resultado_activo_pasivo;

        return resultado_activo_pasivo

    def _Total_ingresos(self, account_res):
        resultado_ingresos_gastos = 0.0
        key_Ingresos = 'Income'
        key_Gastos = 'Expense'
        key_AR = ''
        valor_Ingresos = 0.0
        valor_Gastos = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Ingresos == key_AR:
                    valor_Ingresos = valor_Ingresos + value;

                if key_Gastos == key_AR:
                    valor_Gastos = valor_Gastos + value;

        if valor_Ingresos > valor_Gastos:
            resultado_ingresos_gastos = valor_Ingresos - abs(valor_Gastos);
        else:
            resultado_ingresos_gastos = 0.0

        if valor_Ingresos == resultado_ingresos_gastos:
            resultado_ingresos_gastos = resultado_ingresos_gastos;
        else:
            resultado_ingresos_gastos = valor_Ingresos + resultado_ingresos_gastos;

        return resultado_ingresos_gastos

    def _Total_gastos(self, account_res):
        resultado_gastos_ingresos = 0.0
        key_Ingresos = 'Income'
        key_Gastos = 'Expense'
        key_AR = ''
        valor_Ingresos = 0.0
        valor_Gastos = 0.0

        for account_row in account_res:
            for key, value in account_row.items():
                key_AR = key;
                if key_Ingresos == key_AR:
                    valor_Ingresos = valor_Ingresos + value;

                if key_Gastos == key_AR:
                    valor_Gastos = valor_Gastos + value;

        if valor_Gastos > valor_Ingresos:
            resultado_gastos_ingresos = valor_Gastos - abs(valor_Ingresos);
        else:
            resultado_gastos_ingresos = 0.0

        if valor_Gastos == resultado_gastos_ingresos:
            resultado_gastos_ingresos = resultado_gastos_ingresos;
        else:
            resultado_gastos_ingresos = valor_Gastos + resultado_gastos_ingresos;

        return resultado_gastos_ingresos"""


    def _get_accounts(self, accounts, display_account, enable_negative_values):
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


                # try:
                #
                account_type = str(account_types.get(account.id).get('type'))
                #
                # except AttributeError:
                #     raise Warning('Debe configurar los tipos de cuentas y configurar los informes financieros')

                #  enable negative values

                if enable_negative_values:
                    # res[account_type] = res['balance']  #'Liability', 'Assets', 'Income', 'Expense'
                    if res['balance'] > 0:
                        res['balance_pos'] = res['balance']
                        # verify that account_type belong to (assets/liability)
                        if account_type in ['Assets', 'Liability']:
                            res['Assets'] = abs(res['balance'])
                        elif account_type in ['Income', 'Expense']:
                            res['Expense'] = abs(res['balance'])
                    else:
                        res['balance_neg'] = abs(res['balance'])
                        if account_type in ['Assets', 'Liability']:
                            res['Liability'] = abs(res['balance'])
                        elif account_type in ['Income', 'Expense']:
                            res['Income'] = abs(res['balance'])
                else:
                    res[account_type] = res['balance']  # 'Liability', 'Assets', 'Income', 'Expense'
                    if res['balance'] > 0:
                        res['balance_pos'] = abs(res['balance'])
                    else:
                        res['balance_neg'] = abs(res['balance'])
            if display_account == 'all':
                account_res.append(res)
            if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        enable_negative_values = data['form'].get('enable_negative_values')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts,
                                                                                        display_account,
                                                                                        enable_negative_values)
        Totals, Result = self._compute_total(account_res,enable_negative_values)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
            'Totals': Totals,
            'Result': Result
        }
        return docargs
        # return self.env['report'].render('eightcolumn_balance.report_eightcolumns', docargs)
