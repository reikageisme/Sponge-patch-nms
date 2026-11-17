"""Read-only posttag package/prior-original audit; no device access."""
from pathlib import Path
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'
TAG='925c544f618491e5b21a3621d77804a10686d111'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    prep=json.loads((B/'source_preparation.json').read_text())
    for name,digest in prep['source_sha256'].items():
        raw=(S/name).read_bytes()
        assert sha(S/name)==digest
        assert raw==(B/'registered_materials'/name).read_bytes()
        assert raw==subprocess.check_output(['git','show',f'{TAG}:sponge-sim/studies/pi3b_nms_predecessor_20261115/{name}'],cwd=ROOT)
    old=ROOT/'sponge-sim/results/pi3b_renderer_memory_usb_20261115'
    manifest=json.loads((old/'full_transfer_verification.json').read_text())
    base=old/'runs/memory_full_01/original'
    for name,entry in manifest['files'].items():
        p=base/name
        assert p.resolve().is_relative_to(base.resolve())
        assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],name
    assert sha(ROOT/'paper_en/references.bib')=='58bcb86a185ac4f338168adc894cd9b188d17fe1f1afad510ff05924f38f7d12'
    assert not (S/'functional_activation.json').exists()
    result=dict(status='HOST_ONLY_PASS_NATIVE_NOT_STARTED',supervisor_tag=TAG,
        source_archive_tag_files_matched=23,host_tests_at_tag=64,additional_posttag_fault_tests=5,current_host_tests=69,
        host_log='host_checks_02.log',host_log_sha256=sha(B/'host_checks_02.log'),
        unchanged_prior_rss_full_originals=len(manifest['files']),bib_unchanged=True,
        native_supervisor_qualified=False,functional_activation_present=False,new_empirical_endpoints=0)
    with (B/'offline_final_verification.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))


if __name__=='__main__':main()
