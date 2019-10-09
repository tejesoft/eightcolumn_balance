# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EightColumnWizard(models.TransientModel):
    _name = "eightcolumn.wizard"
    _description = "Eight columns report wizard"

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Fecha desde')
    date_to = fields.Date(string='Fecha hasta')
    target_move = fields.Selection([('posted', 'Todos los publicados'),
                                    ('all', 'Todos'),
                                    ], string='Movimientos', required=False, default='posted')
    display_account = fields.Selection([('all', 'Todas'), ('movement', 'Con movimientos'),
                                        ('not_zero', 'Con balance distinto de cero'), ],
                                       string='Mostrar cuentas', required=False, default='movement')
    enable_negative_values = fields.Boolean('inhabilitar cifras negativas', default=False,
                                            help="esta opcion no mostrará datos negativos(-)")

    def _build_contexts(self, data):
        result = {}
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('eightcolumn_balance.action_report_eightcolumns').report_action([], data=data)
        #return self.env['report'].get_action(records, 'eightcolumn_balance.report_eightcolumns', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'target_move', 'enable_negative_values'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)

    @api.multi
    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        return data
