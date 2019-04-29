# -*- coding: utf-8 -*-
{
    'name' : 'Balance 8 Columnas',
    'version' : '1.0',
    'summary': 'Genera un reporte en formato PDF con el Balance 8 Columnas',
    'sequence': 16,
    'category': 'Accounting',
    'author': u'''Tejesoft Spa''',
    'description': """
Balance 8 Columnas
======================================
Reporte legal que muestra un Balance de 8 Columnas

    """,
    'category': 'Accounting',
    'website': 'http://tejesoft.com',
    'images' : [],
    'depends' : ['base_setup', 'report', 'sale'],
    'data': [
        'wizard/eightcolumn_wizard_view.xml',
        'views/eightcolumn_balance_report.xml',
        'views/report_eightcolumns.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}