import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Dictionary for control family summaries
family_summaries = {
    "ac": "Ensures appropriate access to systems and data based on roles.",
    "at": "Focuses on training and awareness for security and privacy.",
    "au": "Focuses on tracking and reviewing system activities for accountability.",
    "ca": "Deals with assessment, authorization, and monitoring of systems.",
    "cm": "Manages system configurations to maintain security and compliance.",
    "cp": "Ensures contingency planning for system recovery and continuity.",
    "ia": "Handles identification and authentication of users and devices.",
    "ir": "Manages incident response to security breaches and incidents.",
    "ma": "Covers maintenance activities to ensure system security and integrity.",
    "mp": "Protects media containing sensitive information.",
    "pe": "Ensures physical and environmental protection of systems and data.",
    "pl": "Involves planning for security and privacy in system development.",
    "pm": "Manages program-level security and privacy activities.",
    "ps": "Handles personnel security to ensure trustworthiness of staff.",
    "pt": "Deals with processing and transparency of personally identifiable information.",
    "ra": "Assesses risks to systems and data.",
    "sa": "Manages system and services acquisition to ensure security.",
    "sc": "Protects system and communications to maintain confidentiality and integrity.",
    "si": "Ensures system and information integrity through various controls.",
    "sr": "Manages supply chain risks to prevent security breaches."
}

# Dictionary for control summaries (example subset; expand as needed)
control_summaries = {
    "ac-1": "Ensures documented policies and procedures for managing access control.",
    "ac-2": "Manages user accounts to ensure proper access and accountability.",
    "au-1": "Requires policies for auditing system activities.",
    "au-2": "Ensures event logging for accountability and monitoring.",
    # Add more summaries for other controls as needed
}

def load_catalog(file_path):
    """Load the OSCAL control catalog from a JSON file."""
    print(f"Loading catalog from {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)

def catalog_to_html(catalog):
    """Generate an enhanced HTML reference for the OSCAL control catalog."""
    print("Running catalog_to_html - Version 2023-10-20 Enhanced with Collapsible Sidebar")
    html = '<h1>Control Catalog Reference</h1>'
    catalog_title = catalog['catalog']['metadata'].get('title', 'Unnamed Catalog')
    html += f'<h2>{catalog_title}</h2>'

    # Compliance Dashboard (placeholder data)
    controls = catalog['catalog'].get('controls', [])
    groups = catalog['catalog'].get('groups', [])
    total_controls = sum(len(group.get('controls', [])) for group in groups) + len(controls)
    html += f'''
    <div class="compliance-dashboard">
        <h2>Compliance Dashboard</h2>
        <p>Total Controls: {total_controls}</p>
        <p>Implemented: 0 (placeholder)</p>
        <p>In Progress: 0 (placeholder)</p>
        <p>Not Applicable: 0 (placeholder)</p>
    </div>
    '''

    # Search and Filter Options
    html += '''
    <input type="text" id="searchInput" class="search-bar" placeholder="Search controls..." onkeyup="searchControls()">
    <div class="filter-options">
        <label>Filter by Family: </label>
        <select id="familyFilter" onchange="filterControls()">
            <option value="all">All</option>
    '''
    for group in groups:
        html += f'<option value="{group["id"]}">{group["title"]} ({group["id"]})</option>'
    html += '''
        </select>
        <label>Filter by Status: </label>
        <select id="statusFilter" onchange="filterByStatus()">
            <option value="all">All</option>
            <option value="not-implemented">Not Implemented</option>
            <option value="in-progress">In Progress</option>
            <option value="implemented">Implemented</option>
            <option value="not-applicable">Not Applicable</option>
        </select>
    </div>
    '''

    # Table of Contents (Collapsible Sidebar)
    html += '<button id="toggleToc">☰ TOC</button>'
    html += '<div id="tocSidebar" class="toc-sidebar collapsed">'
    html += '<h3>Table of Contents</h3><ul class="toc">'
    for group in groups:
        html += f'<li><a href="#group-{group["id"]}">{group["title"]} ({group["id"]})</a></li>'
        for control in group.get('controls', []):
            html += f'<li style="margin-left: 20px;"><a href="#{control["id"]}">{control["title"]} ({control["id"]})</a></li>'
    for control in controls:
        html += f'<li><a href="#{control["id"]}">{control["title"]} ({control["id"]})</a></li>'
    html += '</ul></div>'

    # Main Content
    html += '<div id="mainContent" class="main-content expanded">'
    if groups:
        html += '<h3>Control Groups</h3>'
        for group in groups:
            html += f'<div class="group" id="group-{group["id"]}">'
            html += f'<h4>{group["title"]} ({group["id"]})</h4>'
            if group["id"] in family_summaries:
                html += f'<p>{family_summaries[group["id"]]}</p>'
            if 'class' in group:
                html += f'<p>Class: {group["class"]}</p>'
            html += control_details(group.get('controls', []))
            html += '</div>'
    html += '<h3>Controls</h3>'
    html += control_details(controls)
    html += '</div>'  # Close mainContent
    return html

def render_part(part, depth=0):
    """Recursively render a part and its nested parts with simplified assessment methods."""
    print(f"Rendering part: {part.get('name', 'Unnamed')} (Depth: {depth})")
    part_id = part.get("id", "N/A")
    html = f'<li><strong>{part["name"]}</strong> (ID: {part_id})'
    if 'prose' in part:
        html += f'<p>{part["prose"]}</p>'
    if 'parts' in part:
        html += '<ul>'
        for sub_part in part['parts']:
            html += render_part(sub_part, depth + 1)
        html += '</ul>'
    if 'links' in part:
        html += f'<p>Related Links: {", ".join(link["href"] for link in part["links"])}</p>'
    if 'assessment-method' in part['name'].lower():  # Check if part is an assessment method
        method_type = part.get('name', 'Unknown').lower()
        if 'examine' in method_type:
            html += '<li><strong>Examine</strong>: Review these documents and records:'
        elif 'interview' in method_type:
            html += '<li><strong>Interview</strong>: Discuss with these personnel:'
        elif 'test' in method_type:
            html += '<li><strong>Test</strong>: Verify these mechanisms or processes:'
        else:
            html += '<li><strong>Assessment Method</strong>:'
        if 'parts' in part:
            html += '<ul>'
            for sub_part in part['parts']:
                if 'prose' in sub_part:
                    html += f'<li>{sub_part["prose"]}</li>'
            html += '</ul>'
        html += '</li>'
    html += '</li>'
    return html

def control_details(controls):
    """Generate HTML for a list of controls with enhancements."""
    html = ''
    for control in controls:
        if "id" not in control:
            print(f"Warning: Control missing 'id' field: {control}")
            continue
        control_id = control["id"]
        print(f"Generating control div for: {control_id}")
        html += f'<div class="control" id="{control_id}" data-family="{control_id.split("-")[0]}" data-original-html="">'
        html += f'<h4 title="{control["title"]}">{control["title"]} ({control_id})</h4>'
        if control_id in control_summaries:
            html += f'<p>{control_summaries[control_id]}</p>'
        if 'class' in control:
            html += f'<p><strong>Class:</strong> {control["class"]}</p>'

        # Properties
        if 'props' in control:
            html += '<p><strong>Properties:</strong></p><ul>'
            for prop in control['props']:
                html += f'<li>{prop["name"]}: {prop["value"]}'
                if 'class' in prop:
                    html += f' (class: {prop["class"]})'
                html += '</li>'
            html += '</ul>'

        # Implementation Guidance with Example
        html += '''
        <p><strong>Implementation Guidance:</strong></p>
        <div class="implementation-guidance">
            <p>Example: For access control, configure role-based access using a tool like AWS IAM or Active Directory.</p>
        </div>
        '''

        # Status Tracking
        html += f'''
        <p><strong>Status:</strong></p>
        <select class="status-select" onchange="updateStatus(this, '{control_id}')">
            <option value="not-implemented">Not Implemented</option>
            <option value="in-progress">In Progress</option>
            <option value="implemented">Implemented</option>
            <option value="not-applicable">Not Applicable</option>
        </select>
        '''

        # Parameters and Parts
        if 'params' in control:
            html += '<details><summary><strong>Parameters</strong></summary><ul>'
            for param in control['params']:
                html += f'<li>ID: {param["id"]}'
                if 'label' in param:
                    html += f' - Label: {param["label"]}'
                html += '</li>'
            html += '</ul></details>'
        
        if 'parts' in control:
            html += '<details><summary><strong>Details</strong></summary><ul>'
            for part in control['parts']:
                html += render_part(part)
            html += '</ul></details>'

        # Related Controls
        if 'links' in control:
            related_controls_html = '<p><strong>Related Controls:</strong> '
            related_controls_html += ', '.join(f'<a href="#{link["href"].lstrip("#")}">{link["href"]}</a>' for link in control['links'] if link.get('rel') == 'related')
            html += related_controls_html + '</p>'

        html += '</div>'
    return html

def select_file():
    """Open file dialog to select the OSCAL catalog JSON file and process it."""
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            catalog = load_catalog(file_path)
            html_content = catalog_to_html(catalog)
            output_file = os.path.splitext(file_path)[0] + '.html'
            with open(output_file, 'w') as f:
                f.write(f"""
<html>
<head>
<title>OSCAL Control Catalog Reference</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
h1, h2, h3, h4 {{ color: #333; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
h4 {{ margin-top: 20px; color: #555; }}
.group, .control {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background-color: #f9f9f9; }}
.toc {{ list-style-type: none; padding-left: 0; }}
.toc li {{ margin: 5px 0; }}
details {{ margin: 10px 0; }}
summary {{ cursor: pointer; font-weight: bold; }}
ul {{ list-style-type: disc; margin-left: 20px; }}
p {{ margin: 5px 0; }}
a {{ color: #0066cc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.search-bar {{ margin: 20px 0; padding: 5px; width: 100%; }}
.filter-options {{ margin: 10px 0; }}
.compliance-dashboard {{ background: #e9f7ef; padding: 15px; border-radius: 5px; }}
.implementation-guidance {{ background: #f0f8ff; padding: 10px; border-radius: 5px; }}
.status-select {{ margin-left: 10px; }}
.toc-sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 25%;
    height: 100%;
    background-color: #f9f9f9;
    overflow-y: auto;
    transition: width 0.3s;
    z-index: 1000;
}}
.main-content {{
    margin-left: 25%;
    transition: margin-left 0.3s;
}}
.toc-sidebar.collapsed {{
    width: 0;
}}
.main-content.expanded {{
    margin-left: 0;
}}
#toggleToc {{
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 1001;
    background-color: #0066cc;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
}}
#toggleToc:hover {{
    background-color: #0056b3;
}}
</style>
<script>
// Function to highlight text in text nodes only
function highlightText(node, searchText, highlightClass) {{
    if (node.nodeType === 3) {{ // Text node
        const text = node.nodeValue;
        const regex = new RegExp(searchText, 'gi');
        if (text.toLowerCase().includes(searchText.toLowerCase())) {{
            const span = document.createElement('span');
            span.innerHTML = text.replace(regex, match => `<span class="${{highlightClass}}">${{match}}</span>`);
            node.parentNode.replaceChild(span, node);
        }}
    }} else if (node.nodeType === 1 && node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {{ // Element node
        for (let i = 0; i < node.childNodes.length; i++) {{
            highlightText(node.childNodes[i], searchText, highlightClass);
        }}
    }}
}}

// Function to restore original HTML and apply highlighting
function searchControls() {{
    var input = document.getElementById('searchInput').value;
    var controls = document.querySelectorAll('.control');
    
    controls.forEach(function(control) {{
        // Restore original HTML if stored
        if (!control.dataset.originalHtml) {{
            control.dataset.originalHtml = control.innerHTML;
        }} else {{
            control.innerHTML = control.dataset.originalHtml;
        }}

        var text = control.textContent.toLowerCase();
        if (input && text.includes(input.toLowerCase())) {{
            control.style.display = '';
            highlightText(control, input, 'highlight');
        }} else {{
            control.style.display = input ? 'none' : '';
        }}
    }});
}}

function filterControls() {{
    var family = document.getElementById('familyFilter').value;
    var controls = document.querySelectorAll('.control');
    controls.forEach(function(control) {{
        var controlFamily = control.getAttribute('data-family');
        control.style.display = (family === 'all' || controlFamily === family) ? '' : 'none';
    }});
}}

function filterByStatus() {{
    var status = document.getElementById('statusFilter').value;
    var controls = document.querySelectorAll('.control');
    controls.forEach(function(control) {{
        var controlStatus = control.querySelector('.status-select').value;
        control.style.display = (status === 'all' || controlStatus === status) ? '' : 'none';
    }});
}}

function updateStatus(select, controlId) {{
    console.log(`Status of ${{controlId}} updated to: ${{select.value}}`);
    // Future: Save status to local storage or backend
}}

document.addEventListener('DOMContentLoaded', function() {{
    var toggleButton = document.getElementById('toggleToc');
    if (toggleButton) {{
        toggleButton.addEventListener('click', function() {{
            var toc = document.getElementById('tocSidebar');
            var content = document.getElementById('mainContent');
            if (toc.classList.contains('collapsed')) {{
                toc.classList.remove('collapsed');
                content.classList.remove('expanded');
            }} else {{
                toc.classList.add('collapsed');
                content.classList.add('expanded');
            }}
        }});
    }}
    // Initial search to apply any default highlighting
    searchControls();
}});
</script>
</head>
<body>
{html_content}
</body>
</html>
""")
            messagebox.showinfo("Success", f"HTML exported to {output_file}")
        except Exception as e:
            import traceback
            print("Error details:")
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("OSCAL Catalog Exporter")
select_button = tk.Button(root, text="Select OSCAL Catalog JSON", command=select_file)
select_button.pack(pady=20)
root.mainloop()
