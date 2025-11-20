{
    'name': 'zzwxrchi SQL Export Custom',
    'version': '16.0.1.0.0',
    'category': 'Reporting',
    'summary': 
        """
        This adons change 2 custom properties output datas:
            Property type Tags:
                Will output with tuple type result(convenient for integration into sql)
                If tag name contains '=', like 'draft=Borrador', the out put will be 'draft'

            Property type Selection
                Will output the input laber name, not the hash number like sql_export original settings
                If the input text contains '=', like '1=A', the out put will be '1'

            With format 'xxx=yyy', the addons use 'xxx' like a key and 'yyy' a value
            If inputs text without '=', don't change anything
        """,
    'author': 'Miguel XL',
    'license': 'AGPL-3',
    'depends': ['sql_export'],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'auto_install': False,
}
