import os
import json
import csv
import argparse
import urllib.parse
import qrcode

import utilities as utils



CONFIG = utils.load_config()


def generate_qr_code(link):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(link)
    qr.make(fit=True)
    return qr


def save_qr_code(qr, destination, name):
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(destination + '/' + name, 'JPEG')


def generate_link_for_csv_row(row):
    branch_key = CONFIG['account_parameters']['branch_key']
    link_domain = CONFIG['account_parameters']['link_domain']

    # Custom domains require a Branch key and an /a/ on the URL path.
    is_custom_domain = not 'app.link' in link_domain
    base_url =''

    if is_custom_domain:
        base_url = 'https://{}/a/{}/'.format(link_domain, branch_key)
    else:
        base_url = 'https://{}/'.format(link_domain)

    # Keys (fields) that have been specified in the config file that need to be
    # included. Ignore the potential keys that don't have data behind them.
    # E.g. someone may have left "feature" blank, so don't add it to the URL.
    target_keys = []
    for item in CONFIG['link_parameters']:
        if CONFIG['link_parameters'][item]:
            target_keys.append(item)

    # Pass in values of tuples to handle the case where ~tags repeats
    # more than once in a request.
    query_params = []
    # For each key to be added as a query param.
    for key in target_keys:
        if key == '~tags':
            # Tags should be separated by a ";" in the csv file.
            values = row[CONFIG['link_parameters'][key]].split(';')
            for value in values:
                query_params.append((key, value))
        else:
            query_params.append((key, row[CONFIG['link_parameters'][key]]))

    encoded_query_params = urllib.parse.urlencode(query_params)
    final_link = base_url + '?' + encoded_query_params
    return final_link


def generate_links_from_file(file):
    links = []

    with open(file) as csv_file:
        reader = csv.DictReader(csv_file)

        # For each entry in the CSV file.
        for row in reader:
            link = generate_link_for_csv_row(row)
            links.append(link)

    return links


def generate_qr_code_from_csv(file, output_dir):
    with open(file) as csv_input_file:
        reader = csv.DictReader(csv_input_file)
        column_names = reader.fieldnames

        with open(output_dir + '/links/output.csv', 'w') as csv_output_file:
            column_names.append('link')
            writer = csv.DictWriter(csv_output_file, fieldnames=column_names)
            writer.writeheader()

            for row in reader:
                link = generate_link_for_csv_row(row)
                final_row = row
                final_row['link'] = link
                writer.writerow(final_row)

                # We use the "csv_id_row" field from the config file to create
                # a name for the QR code image file that allows it to be
                # matched up with this corresponding row in the output csv file.
                unique_image_name = row[CONFIG['meta_parameters']['csv_id_row']]

                qr = generate_qr_code(link)
                save_qr_code(qr, output_dir + '/qr_codes', '{}.jpeg'.format(unique_image_name))


def build_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--input', default='../stores.csv', help='The input CSV file containing data for link creation.')
    parser.add_argument('-o', '--output', default='../output', help='The directory to save output values into. This directory should contain "links" and "qr_codes" subdirectories.')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    csv_file = args.input
    output_dir = args.output

    generate_qr_code_from_csv(csv_file, output_dir)


if __name__ == '__main__':
    main()
