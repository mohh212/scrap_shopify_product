from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
from io import BytesIO

app = Flask(__name__)

@app.route('/shopify-to-csv', methods=['POST'])
def shopify_to_csv():
    try:
        data = request.json
        url = data.get("url")
        nom_file = data.get("filename", "products")

        if not url:
            return jsonify({"error": "URL manquante"}), 400

        url += "/products.json"
        response = requests.get(url)
        response.raise_for_status()
        data_json = response.json()

        products_list = []

        for product in data_json['products']:
            handle = product.get('handle', "")
            title = product.get('title', "")
            body_html = product.get('body_html', "")
            vendor = product.get('vendor', "")
            product_type = product.get('product_type', "")
            tags = ", ".join(product.get('tags', []))
            published = "TRUE"
            images = product.get('images', [])
            first_image_src = images[0]['src'] if images else ""
            options = product.get('options', [])

            for variant in product.get('variants', []):
                row = {
                    "Handle": handle,
                    "Title": title,
                    "Body (HTML)": body_html,
                    "Vendor": vendor,
                    "Type": product_type,
                    "Tags": tags,
                    "Published": published,
                    "Option1 Name": options[0]['name'] if len(options) > 0 else "",
                    "Option1 Value": variant.get('option1', ""),
                    "Option2 Name": options[1]['name'] if len(options) > 1 else "",
                    "Option2 Value": variant.get('option2', ""),
                    "Option3 Name": options[2]['name'] if len(options) > 2 else "",
                    "Option3 Value": variant.get('option3', ""),
                    "Variant SKU": variant.get('sku', ""),
                    "Variant Grams": variant.get('grams', 0),
                    "Variant Inventory Tracker": variant.get('inventory_management', ""),
                    "Variant Inventory Qty": variant.get('inventory_quantity', 0),
                    "Variant Inventory Policy": variant.get('inventory_policy', ""),
                    "Variant Fulfillment Service": variant.get('fulfillment_service', ""),
                    "Variant Price": variant.get('price', ""),
                    "Variant Compare At Price": variant.get('compare_at_price', ""),
                    "Variant Requires Shipping": variant.get('requires_shipping', True),
                    "Variant Taxable": variant.get('taxable', True),
                    "Variant Barcode": variant.get('barcode', ""),
                    "Image Src": first_image_src,
                    "Image Position": 1,
                    "Image Alt Text": "",
                    "Gift Card": "FALSE",
                    "Status": "active"
                }
                products_list.append(row)

        df = pd.DataFrame(products_list)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)

        return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=f"{nom_file}.csv")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
