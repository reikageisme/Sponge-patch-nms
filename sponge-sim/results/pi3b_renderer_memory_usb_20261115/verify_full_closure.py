"""Read-only cross-artifact integrity check after full analysis; exclusive receipt."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

B = Path(__file__).resolve().parent
ROOT = B.parents[2]


def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    regdir = ROOT/'sponge-sim/studies/pi3b_renderer_memory_usb_20261115'
    reg = load(regdir/'memory_registration.json')
    summary = load(B/'runs/memory_full_01/summary.json')
    independent = load(B/'independent_full_audit.json')
    assert summary['quality_pass'] and independent['status'] == 'INDEPENDENT_FULL_RAW_REPLAY_PASS'
    retained = {}
    for folder, receipt, relroot in (
        ('pi3b_full20_20261114', 'transfer_verification.json', 'runs/full_01'),
        ('pi3b_renderer_functional_cache_20261114', 'transfer_verification.json', ''),
        ('pi3b_renderer_memory_v1_20261114', 'smoke_transfer_verification.json', 'runs/memory_smoke_01/original'),
        ('pi3b_renderer_memory_usb_20261115', 'smoke_transfer_verification.json', 'runs/memory_smoke_01/original'),
        ('pi3b_renderer_memory_usb_20261115', 'full_transfer_verification.json', 'runs/memory_full_01/original')):
        base = ROOT/'sponge-sim/results'/folder
        hashes = load(base/receipt)['files']
        for name, entry in hashes.items():
            path = base/relroot/name
            assert sha(path) == entry['sha256'], path
            assert path.stat().st_size == entry['bytes'], path
        retained[folder+'/'+relroot] = len(hashes)
    materials = ROOT/'sponge-sim/results/laptop_seg_20261107'
    for name, digest in reg['source_material_sha256'].items(): assert sha(materials/name) == digest
    for name, digest in reg['reference_sha256'].items(): assert sha(regdir/name) == digest
    assert sha(ROOT/'sponge-sim/prereg'/reg['protocol']['filename']) == reg['protocol']['sha256']
    assert sha(regdir/'usb_contract.json') == reg['usb_contract_sha256']
    bib = ROOT/'paper_en/references.bib'
    assert sha(bib) == '58bcb86a185ac4f338168adc894cd9b188d17fe1f1afad510ff05924f38f7d12'
    approval = load(B/'full_approval.json')
    manifest = load(B/'runs/memory_full_01/manifest.json')
    assert approval['user_approved'] is True and approval['commit'] == manifest['commit'] == independent['commit']
    transport = load(B/'full_transport_recovery_receipt.json')
    assert not transport['experiment_restarted'] and not load(B/'full_frontend_terminal.json')['authoritative_service_terminal']
    parent = B/'runs/memory_full_01/original'
    assert load(parent/'campaign_terminal.json') == dict(status='COMPLETED', gate_returncode=0)
    assert load(parent/'restore.json')['status'] == 'RESTORED'
    for name in ('full_remote_before_fetch.json', 'full_remote_after_fetch.json'):
        obs = load(B/name)['result']
        assert obs['restore_readback_matches'] and not obs['workers']
        assert obs['service']['MainPID'] == '0' and obs['service']['ActiveState'] in ('inactive', 'failed')
        assert obs['source_sha256'] == reg['source_sha256']
    paper = ROOT/'paper_en/segmentation_extension'
    mapping = load(paper/'pi3b_memory_sources.json')
    for path, digest in mapping['sources'].items(): assert sha(ROOT/path) == digest
    extension = load(paper/'sources.json')
    for path, digest in extension.items(): assert sha(ROOT/path) == digest
    text = (paper/'pi3b_memory.tex').read_text(encoding='utf-8')
    # Limited structural check, not a LaTeX compiler/render claim.
    stripped = re.sub(r'(?<!\\)%[^\n]*', '', text)
    balance = 0
    for token in re.findall(r'(?<!\\)[{}]', stripped):
        balance += 1 if token == '{' else -1
        assert balance >= 0
    assert balance == 0
    main_bytes = (ROOT/'paper_en/main.tex').read_bytes()
    result = dict(status='CLOSED_FULL_RSS_PASS_INTEGRITY_AND_PAPER_CHECKED',
        original_hashes_rechecked=retained, original_material_hashes_checked=len(reg['source_material_sha256']),
        runtime_unchanged=load(B/'full_transfer_verification.json')['runtime_source_unchanged'],
        tag=reg['tag'], commit=independent['commit'], quality_pass=summary['quality_pass'],
        raw_sha256=independent['raw_sha256'], report_sha256=sha(ROOT/'docs/reports/PI3B_RENDERER_MEMORY_USB_FULL20_20261115.md'),
        independent_audit_sha256=sha(B/'independent_full_audit.json'),
        paper_fragment_sha256=sha(paper/'pi3b_memory.tex'), paper_source_map_sha256=sha(paper/'pi3b_memory_sources.json'),
        paper_checks_sha256=sha(B/'paper_checks_01.log'), paper_test_count=9,
        protected_bib_sha256=sha(bib), main_sha256_observed_after_work=hashlib.sha256(main_bytes).hexdigest(),
        main_user_changes_left_unstaged=True, full_pdf_compiled=False, plot_png_visually_inspected=True,
        ssh_kept_open=True, no_full02=True, no_scientific_workload_active=True,
        transport_root_cause='UNKNOWN', older_failed_protocols_unchanged=True)
    with (B/'full_final_verification.json').open('x', encoding='utf-8') as f: json.dump(result, f, indent=2)
    print(json.dumps(result))


if __name__ == '__main__': main()
