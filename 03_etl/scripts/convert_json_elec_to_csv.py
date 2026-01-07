import json
import csv
import os
import glob

def convert_elec_json_to_csv():
    input_dir = r"D:\BI\01_operational_sources\json"
    output_file = r"D:\BI\03_etl\staging\extracted\elec_consumption_extracted.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_region', 'id_batiment', 'type_energie', 'unite', 'date_generation', 'compteur_id', 'date_mesure', 'consommation_kWh']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        json_files = glob.glob(os.path.join(input_dir, "Élec_consumption_*.json"))
        
        for json_file in sorted(json_files):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                id_region = data['id_region']
                
                for batiment in data['batiments']:
                    id_batiment = batiment['id_batiment']
                    type_energie = batiment['type_energie']
                    unite = batiment['unite']
                    date_generation = batiment['date_generation']
                    
                    for mesure in batiment['mesures']:
                        row = {
                            'id_region': id_region,
                            'id_batiment': id_batiment,
                            'type_energie': type_energie,
                            'unite': unite,
                            'date_generation': date_generation,
                            'compteur_id': mesure['compteur_id'],
                            'date_mesure': mesure['date_mesure'],
                            'consommation_kWh': mesure['consommation_kWh']
                        }
                        writer.writerow(row)

if __name__ == "__main__":
    convert_elec_json_to_csv()
    print("Conversion Élec terminée !")