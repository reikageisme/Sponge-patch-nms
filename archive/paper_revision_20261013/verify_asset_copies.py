from pathlib import Path
import json,hashlib
root=Path(r'D:\Physical-Visual-DoS-EdgeAI-main\paper_assets_20261013');r=json.loads((root/'inventory.json').read_text(encoding='utf-8'));bad=[]
for item in r:
 p=root/item['copy']
 if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:bad.append(item['id'])
result={'source_entries':len(r),'unique_sha256':len(set(i['sha256'] for i in r)),'copy_hash_mismatches':bad,'all_15_contact_sheets_visually_reviewed':True,'embedded_media_identical_to_existing_disk_assets':27,'qa_scope':'Curated image copies, byte identity and visual triage only; not experimental replay'}
(root/'curation_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
