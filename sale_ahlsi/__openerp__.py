# -*- coding: utf-8 -*-
{
    'name': "AHLSI Sale",
    'version': '8.0.0.0.1',
    'author': "Deutsche Motorgerate Inc.",
    'website': "http://www.dmi.com.ph",
    'category': 'stock',
    'depends': [
		'sale','sale_stock'
    ],
    'data': [
        'views/sale_view.xml',
        'views/report_saleorder.xml'
    ],
    
    'installable': True,
    'auto_install': False,
}
