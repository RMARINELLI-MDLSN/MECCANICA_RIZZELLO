import time
import sys
import json
import logging

import stomp

json_serial = "123"
my_json = """{
    "Name": "Jennifer Smith",
    "Contact Number": 7867567898,
    "Email": "jen123@gmail.com",
    "Hobbies":["Reading", "Sketching", "Horse Riding"]
    }"""

my_json2 = """{
        "settings": {
                "serial": "1",
                "status": "2",
                "version": "3"
        },
        "config": {
                "active": "4",
                "version": "5"
        }
}"""


my_json3 = """
{
"action": "INS",
"entity": "ORD",
"rows":
    [
        {
        "materiali_ordini":
            {
            "rows":
                [
                    {
                    "columns":
                        [
                            {
                            "name": "ordine",
                            "value": "ODP-CUTT-30"
                            },
                            {
                            "name": "operazione",
                            "value": "10"
                            },
                            {
                            "name": "sequenza",
                            "value": 5
                            },
                            {
                            "name": "part_number",
                            "value": "00005AUXI0000001"
                            },
                            {
                            "name": "alt_part_number",
                            "value": "0"
                            },
                            {
                            "name": "magazzino",
                            "value": "MP"
                            },
                            {
                            "name": "um_quantita",
                            "value": "ML"
                            },
                            {
                            "name": "quantita",
                            "value": 540.0
                            },
                            {
                            "name": "qta_prelevata",
                            "value": 0.0
                            },
                            {
                            "name": "data_prelievo",
                            "value": "2021-02-16T00:00:00Z"
                            },
                            {
                            "name": "descrizione",
                            "value": "INOX AISI 303 TONDO D.80 LAMIN ATO..."
                            }
                        ]
                    }
                ]
            },
        "operazioni":
            {
            "rows":
                [
                    {
                    "columns":
                        [
                            {
                            "name": "ordine",
                            "value": "ODP-CUTT-30"
                            },
                            {
                            "name": "operazione",
                            "value": "10"
                            },
                            {
                            "name": "sequenza",
                            "value": 10
                            },
                            {
                            "name": "fase",
                            "value": "NULL"
                            },
                            {
                            "name": "descrizione",
                            "value": "NULL"
                            },
                            {
                            "name": "qta_richiesta",
                            "value": 150
                            },
                            {
                            "name": "qta_completata",
                            "value": 0.0
                            },
                            {
                            "name": "qta_base",
                            "value": 1.0
                            },
                            {
                            "name": "centro_assegnato",
                            "value": "LINEA01"
                            },
                            {
                            "name": "macchina_assegnata",
                            "value": "LINEA01"
                            },
                            {
                            "name": "t_lavoro_mac",
                            "value": 0.0
                            },
                            {
                            "name": "t_lavoro_man",
                            "value": 0.0
                            },
                            {
                            "name": "teff_lavoro_mac",
                            "value": 0.0
                            },
                            {
                            "name": "teff_lavoro_man",
                            "value": 0.0
                            },
                            {
                            "name": "t_setup_mac",
                            "value": 0.0
                            },
                            {
                            "name": "t_setup_man",
                            "value": 0.0
                            },
                            {
                            "name": "teff_setup_mac",
                            "value": 0.0
                            },
                            {
                            "name": "teff_setup_man",
                            "value": 0.0
                            }
                        ]
                    }
                ]
            },
        "ordini":
            {
            "columns":
                [
                    {
                    "name": "ordine",
                    "value": "ODP-CUTT-30"
                    },
                    {
                    "name": "part_number",
                    "value": "00005AUXI0000001"
                    },
                    {
                    "name": "faltpnumb",
                    "value": "0"
                    },
                    {
                    "name": "magazzino",
                    "value": "NULL"
                    },
                    {
                    "name": "lotto",
                    "value": "NULL"
                    },
                    {
                    "name": "qta_richiesta",
                    "value": 150
                    },
                    {
                    "name": "qta_completata",
                    "value": 0
                    },
                    {
                    "name": "data_emissione",
                    "value": "2024-04-16T00:00:00Z"
                    },
                    {
                    "name": "frqstdate",
                    "value": "2024-04-16T00:00:00Z"
                    },
                    {
                    "name": "frqduedate",
                    "value": "2024-04-16T00:00:00Z"
                    },
                    {
                    "name": "cliente",
                    "value": "VERSACE"
                    },
                    {
                    "name": "commessa",
                    "value": "prova"
                    },
                    {
                    "name": "stato",
                    "value": "REL"
                    },
                    {
                    "name": "alt_ciclo",
                    "value": 0
                    },
                    {
                    "name": "tipo",
                    "value": "MAKE"
                    },
                    {
                    "name": "cod_ciclo",
                    "value": "CYC-VECTOR"
                    },
                    {
                    "name": "descrizione",
                    "value": "Ordine per CutterIQ50"
                    },
                    {
                    "name": "REPARTO",
                    "value": "PRODUZIONE"
                    }
                ]
            }
        }
    ]
}"""

my_json3_bkp = """
{
"action": "INS",
"entity": "ORD",
"rows":
    [
        {
        "operazioni":
            {
            "rows":
                [
                    {
                    "columns":
                        [
                            {
                            "name": "ordine",
                            "value": "ODP-CUTT-10"
                            },
                            {
                            "name": "operazione",
                            "value": "10"
                            }
                        ]
                    }
                ]
            },
        "ordini":
            {
            "columns":
                [
                    {
                    "name": "ordine",
                    "value": "ODP-CUTT-10"
                    },
                    {
                    "name": "part_number",
                    "value": "LP-CAPF-SAMMY"
                    }
                ]
            }
        }
    ]
}"""

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler

handler = logging.FileHandler("C:\\Users\\MESUser\\PycharmProjects\\PythonProject\\ERP-NP.log")
handler.setLevel(logging.INFO)

# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger

logger.addHandler(handler)

logger.info('ERP-NP')

payload_temp=json.loads(my_json3)
print(payload_temp["rows"][0]["operazioni"]["rows"][0]["columns"][0]["name"])
print(payload_temp["rows"][0]["operazioni"]["rows"][0]["columns"][0]["value"])
print(payload_temp["rows"][0]["operazioni"]["rows"][0]["columns"][1]["name"])
print(payload_temp["rows"][0]["operazioni"]["rows"][0]["columns"][1]["value"])
print("-------------\n")
print(payload_temp["rows"][0]["ordini"]["columns"][0]["name"])
print(payload_temp["rows"][0]["ordini"]["columns"][0]["value"])
print(payload_temp["rows"][0]["ordini"]["columns"][1]["name"])
print(payload_temp["rows"][0]["ordini"]["columns"][1]["value"])

print(my_json3)

#payload_temp["settings"]["serial"]="7"
#print(payload_temp["settings"]["serial"])

#conn = stomp.Connection([('192.168.1.198', 61613)])
#conn = stomp.Connection12(auto_content_length=False)
conn = stomp.Connection12([('192.168.1.198', 61613)], auto_content_length=False)
conn.set_listener('', MyListener())
conn.connect('admin', 'admin', wait=True)
conn.subscribe(destination='ERP-NP', id=1, ack='auto')
conn.send(body=my_json3, destination='ERP-NP',content_type='text/json')
time.sleep(2)
conn.disconnect()