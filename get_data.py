import requests
import pandas as pd
import json
import os
import sys
import argparse
import datetime
import time

def clean_json(item_json):
    keys_with_error = [key for key in item_json if '.' in key]
    for key in keys_with_error:
        item_json[key.replace('.', '_')] = item_json[key]
        item_json.pop(key, None)
    return item_json

parser = argparse.ArgumentParser()
parser.add_argument('url', help="Direccion del servicio Web")
parser.add_argument("-d", "--dir", help="Directorio donde se van a grabar los datos", default = ".")
parser.add_argument("-s", "--sep", help="Separador de los campos (Solo CSV)", default = "|")
parser.add_argument("-i", "--item", help="Elemento de la respuesta donde se encuentran los datos")
parser.add_argument("-n", "--name", help="Nombre del fichero")
parser.add_argument("-f", "--format", help="Formato de los datos (json o csv)", default = "json")
parser.add_argument("-t", "--timestamp", help="Inserta una marca de tiempo en los datos", action='store_true', default = False)
parser.add_argument("-e", "--header", help="Elimina la cabecera del fichero (Solo CSV)", action='store_true', default = False)
args = parser.parse_args()

if args.url is None:
    parser.error("Es necesario especificar la direccion del servicio web!")
    sys.exit(1)

valid_formats = ["csv", "json"]
if args.format not in valid_formats:
    parser.error("Error en el formato de los datos. Valores validos: %s" % ','.join(valid_formats))
    sys.exit(1)

if args.name is None:
    args.name = "%s-%s" % (os.path.basename(os.path.normpath(args.url)), time.strftime("%Y%m%d%H%M%S"))

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

fileName = "%s/%s.%s" % (args.dir, args.name, args.format)
print("Getting item_json from %s" % args.url)
print("File output: %s" % fileName)

try:
    response = requests.get(args.url)
except Exception as e:
    print("Problems with the url: %s" % e.__doc__)
    sys.exit(1)

if not response.ok:
    print("Request incorrect: %s" % response.reason)
    sys.exit(1)


response_json = response.json()
if args.item and (args.item in response_json):
    response_json = response_json[args.item]

timestamp_str = datetime.datetime.now().isoformat()

if args.format == "json":
    with open(fileName, 'w') as file:
        for item_json in response_json:
            if args.timestamp:
                item_json['_timestamp'] = timestamp_str

            json.dump(clean_json(item_json), file)
            file.write(os.linesep)

if args.format == "csv":
    df = pd.DataFrame(response_json)
    if args.timestamp:
        df = df.assign(_timestamp = timestamp_str)

    df.to_csv(fileName, index=False, header=not args.header, decimal='.', sep= args.sep, encoding='utf-8')
