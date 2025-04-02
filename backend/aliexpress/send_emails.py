import pytoolsx as pt

shared_styles = """
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        padding: 20px;
    }
    .container {
        max-width: 600px;
        background: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    p {
        font-size: 16px;
        line-height: 1.6;
        text-align: left;
    }
    .highlight {
        font-weight: bold;
        color: #333;
    }
    .button {
        display: inline-block;
        padding: 10px 20px;
        margin: 10px 5px;
        font-size: 14px;
        color: white;
        text-decoration: none;
        border-radius: 5px;
    }
    .ali-button {
        background-color: #007bff;
    }
    .dropvault-button {
        background-color: #e72330;
    }
"""

def send_success_email(order_info, recipient):
    subject = f"✅ Order Resolved & Shipped: {order_info.get('order_id')}"

    body = f"""
    <html>
    <head>
        <style>
            {shared_styles}
            h2 {{
                color: #2e7d32;
            }}
            .button {{
                background-color: #28a745;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🎉 Order Recovered & Shipped</h2>
            <p><span class="highlight">Customer:</span> {order_info.get('full_name', 'N/A')}</p>
            <p><span class="highlight">Item:</span> {order_info.get('item_title', 'N/A')}</p>
            <p><span class="highlight">Variant:</span> {order_info.get('ali_value', 'Default')}</p>
            <p><span class="highlight">Variant:</span> {order_info.get('quantity', '0')}</p>
            <p style="margin-top: 20px;">✅ <em>This order previously failed, but has now been fulfilled and shipped.</em></p>
            <a href="http://82.42.112.27:5500/" class="button">View on Dropvault</a>
        </div>
    </body>
    </html>
    """

    pt.send_mail(subject, body, recipient)


def send_failure_email(order_info, recipient):
    subject = f"🚨 Order Failed: {order_info.get('order_id')}"

    body = f"""
    <html>
    <head>
        <style>
            {shared_styles}
            h2 {{
                color: #d32f2f;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🚨 Shipment Failed</h2>
            <p><span class="highlight">Customer:</span> {order_info.get('full_name', 'N/A')}</p>
            <p><span class="highlight">Failure Reason:</span> {order_info.get('fail_reason', 'Unknown failure')}</p>
            <p><span class="highlight">Item:</span> {order_info.get('item_title', 'N/A')}</p>
            <p><span class="highlight">Variant:</span> {order_info.get('ali_value', 'Default')}</p>
            <p style="margin-top: 20px;">📌 <em>Please check the failed shipments log for further details.</em></p>
            <a href="{order_info.get('item-url', '#')}" class="button ali-button">AliExpress Item</a>
            <a href="http://82.42.112.27:5500/" class="button dropvault-button">View on DropVault</a>
        </div>
    </body>
    </html>
    """

    pt.send_mail(subject, body, recipient)