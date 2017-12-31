# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import csv
from StringIO import StringIO
import base64

from openerp.osv import fields, orm, osv


class sql_report_wizard(orm.TransientModel):
    """Will launch general ledger report and pass required args"""

    _name = "sql.report.wizard"


    _columns = {
        'sql_request_id': fields.many2one('sql.request', string="Requête SQL"),
        'sql': fields.text('SQL',required=True),

    }

    def onchange_sql_request(self, cr, uid, ids, sql_request_id, context=None):
        if sql_request_id:
            sql = self.pool.get('sql.request').browse(cr,uid,sql_request_id).sql
            return {'value': {'sql': sql}}

        else:
            return True


    def export_report(self, cr, uid, ids, context=None):
        wizard_record = self.pool.get('sql.report.wizard').browse(cr,uid,ids[0])
        sql_to_execute = wizard_record.sql	# Récupère la requête sous forme de text
        select = sql_to_execute[:6].lower()
        if select != 'select' :
            raise osv.except_osv('Autorisation','requête non autorisée')
        try:
            cr.execute(sql_to_execute)
        except:
            raise osv.except_osv('Erreur','Requête sql erronée')
        result = cr.dictfetchall() 
	print (result[0].keys())
        f = StringIO()
   	file_name = wizard_record.sql_request_id.name+".csv"
        #csv_file = csv.writer(f)
        csv_file = csv.writer(f,delimiter=';')
        
        #L'idée de prendre la variable result qui est ensemble de dictionnaire dans un dictionnaire
        #Etape 1: D'
        keys_list=[]
        for key in result[0].keys():	#Pou
#            print(key)			#key represent les noms de colonne
            keys_list.append(key)
        csv_file.writerow(keys_list)
        for res in result:		# res est un élément du dictionnaire résult
            data = []
            #print(res)
            for key in res.keys():
                #print (res[key])  
                data.append(res[key])   
            csv_file.writerow(data)
        #print(keys_list)	
        vals={'data':base64.b64encode(f.getvalue()),'name_file':file_name}
        wizard_id = self.pool.get('sql.file.get.wizard').create(cr, uid, vals)

        return {
            'name':"Export CSV",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'sql.file.get.wizard',
            'res_id':wizard_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            }

sql_report_wizard()

class sql_file_get_wizard(orm.TransientModel):
    _name = 'sql.file.get.wizard'

    _columns = {
        'name_file': fields.char('Nom fichier'),
        'data': fields.binary('Fichier'),

    }

sql_file_get_wizard()
