import re

def parse_iot_html(html_content):
    data = {}
    
    # Regex patterns based on the HTML structure
    patterns = {
        "mean_val": r'<span class="value-label">Mean Value</span><span class="value-num mean">([\d\.]+)</span>',
        "std_val": r'<span class="value-label">Standard Deviation</span><span class="value-num stddev">([\d\.]+)</span>',
        "peak_amp": r'<span class="value-label">Peak Amplitude</span><span class="value-num peak">([\d\.]+)</span>',
        "heart_rate": r'<span class="value-label">Heart Rate</span><span class="value-num heart">([\d\.]+)</span>',
        "rr_var": r'<span class="value-label">RR Variance</span><span class="value-num rr">([\d\.]+)</span>',
        "entropy": r'<span class="value-label">Entropy</span><span class="value-num entropy">([\d\.]+)</span>',
        "prediction": r'<span class="value-label">Result</span><span class="value-num result">(\w+)</span>'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, html_content)
        if match:
            val = match.group(1)
            # Convert to float if numeric
            if key != "prediction":
                try:
                    data[key] = float(val)
                except:
                    data[key] = 0.0
            else:
                data[key] = val
    
    return data

# Test with the saved source.html
try:
    with open("source.html", "r", encoding="utf-8") as f:
        content = f.read()
        extracted = parse_iot_html(content)
        print("Extracted Data:", extracted)
except Exception as e:
    print(e)
