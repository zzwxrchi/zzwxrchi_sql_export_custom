Is a addons for odoo community v16.0.

This adons overwirte sql_export addons behave, change 2 custom properties output datas.

            Property type Tags:
                Will output with tuple type result(convenient for integration into sql)
                If tag name contains '=', like 'draft=Borrador', the out put will be 'draft'

            Property type Selection:
                Will output the input laber name, not the hash number like sql_export original settings
                If the input text contains '=', like '1=A', the out put will be '1'

            With format 'xxx=yyy', the addons use 'xxx' like a key and 'yyy' a value.
            If inputs text without '=', will output with text original, don't change it.
            Is posible need change your created sql statement.
