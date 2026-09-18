#!/usr/bin/env python3
"""
Convert .list rule files to native Egern YAML rulesets.
Outputs to rule/egern/{base_name}.yaml or {base_name}_Domain.yaml / {base_name}_IP.yaml.
"""
import os
import sys

def convert_list_to_egern(list_path):
    with open(list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    suffixes = []
    domains = []
    keywords = []
    cidrs = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        rule_type = parts[0].upper()
        val = parts[1]
        
        if rule_type in ('DOMAIN-SUFFIX', '+.'):
            suffixes.append(val)
        elif rule_type == 'DOMAIN':
            domains.append(val)
        elif rule_type == 'DOMAIN-KEYWORD':
            keywords.append(val)
        elif rule_type in ('IP-CIDR', 'IP-CIDR6', 'IP'):
            cidrs.append(val)
            
    return sorted(set(domains)), sorted(set(suffixes)), sorted(set(keywords)), sorted(set(cidrs))

def write_egern_yaml(out_path, domains, suffixes, keywords, cidrs):
    lines = []
    if cidrs and not (domains or suffixes or keywords):
        lines.append('no_resolve: true')
    if domains:
        lines.append('domain_set:')
        for d in domains:
            lines.append(f'  - {d}')
    if suffixes:
        lines.append('domain_suffix_set:')
        for s in suffixes:
            lines.append(f'  - {s}')
    if keywords:
        lines.append('domain_keyword_set:')
        for k in keywords:
            lines.append(f'  - {k}')
    if cidrs:
        lines.append('ip_cidr_set:')
        for c in cidrs:
            lines.append(f'  - {c}')
            
    content = '\n'.join(lines) + '\n'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Generated {out_path} ({len(domains)} domains, {len(suffixes)} suffixes, {len(keywords)} keywords, {len(cidrs)} cidrs)')

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rule_dir = os.path.join(repo_root, 'rule')
    egern_dir = os.path.join(rule_dir, 'egern')
    
    files = ['Custom_Direct', 'Custom_Proxy', 'Steam_CDN', 'Encrypted_DNS', 'Talkatone', 'Lan']
    for name in files:
        list_file = os.path.join(rule_dir, f'{name}.list')
        if not os.path.exists(list_file):
            continue
        domains, suffixes, keywords, cidrs = convert_list_to_egern(list_file)
        
        # Output domain-only and ip-only variants if both exist
        if (domains or suffixes or keywords) and cidrs:
            write_egern_yaml(os.path.join(egern_dir, f'{name}_Domain.yaml'), domains, suffixes, keywords, [])
            write_egern_yaml(os.path.join(egern_dir, f'{name}_IP.yaml'), [], [], [], cidrs)
        elif cidrs:
            write_egern_yaml(os.path.join(egern_dir, f'{name}_IP.yaml'), [], [], [], cidrs)
            write_egern_yaml(os.path.join(egern_dir, f'{name}.yaml'), domains, suffixes, keywords, cidrs)
        else:
            write_egern_yaml(os.path.join(egern_dir, f'{name}_Domain.yaml'), domains, suffixes, keywords, [])
            write_egern_yaml(os.path.join(egern_dir, f'{name}.yaml'), domains, suffixes, keywords, [])

if __name__ == '__main__':
    main()
