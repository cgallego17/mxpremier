with open('backoffice/templates/backoffice/jugadores/form.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
new_lines = lines[:152]
new_lines.append('  checkbox.addEventListener("change", toggleSegunda);\n')
new_lines.append('  toggleSegunda();\n')
new_lines.append('</script>\n')
new_lines.append('{% endblock %}\n')
with open('backoffice/templates/backoffice/jugadores/form.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Simplified backoffice form JavaScript')
