# Adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/register_memory.py:1-50
# SHA256 11ba8dc6ac70262b4bd178b43e5ddf3050b008dac6fe50376186483f63ea9c06; registered USB-present condition, qualified runtime unchanged.
"""Create the prospective scientific registration once; no device/load/endpoint."""
from pathlib import Path
import hashlib
import json
from memory_worker import SOURCE_FILES,IMAGE_IDS,ARMS,PHASES,CACHE_DIRECTORY,registration

HERE=Path(__file__).resolve().parent
SIM=HERE.parents[1]
TAG='prereg-pi3b-renderer-memory-usb-20261115'
PROTOCOL='PREREG_PI3B_RENDERER_MEMORY_USB_20261115.md'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    qa=SIM/'results/pi3b_renderer_usb_integration_qa_20261115'
    verified=json.loads((qa/'final_verification.json').read_text())
    prepared=json.loads((qa/'source_preparation.json').read_text())
    assert verified['status']=='USB_RUNNER_INTEGRATION_HOST_AND_SLEEP_QA_VERIFIED'
    assert verified['original_files_verified']==44 and verified['independent_restore_readback'] is True
    assert not verified['empirical_endpoint_recorded']
    for name in SOURCE_FILES:assert sha(HERE/name)==prepared['source_sha256'][name]
    manifest=json.loads((HERE/'cache_manifest.json').read_text())
    value=dict(experiment='PI3B-RENDERER-MEMORY-USB',status='PREREGISTERED',tag=TAG,
        arms=list(ARMS),repeats=3,pixel_budget=16_000_000,cpus=[0,1,2,3],interop_threads=1,
        image_ids=IMAGE_IDS,seed=20261114,conditions=['clean','adv'],phases=PHASES,
        cache_directory=CACHE_DIRECTORY,cache_manifest_sha256=sha(HERE/'cache_manifest.json'),
        child_timeout_seconds=180,versions=dict(torch='2.15.0+cpu',numpy='2.5.4',python='3.13.5'),
        governor='powersave',gates=dict(clock_hz=[594000000,606000000],abort_temp_c=75,
            abort_mem_available_kb=40000,aa_abs_log=.02,mde_log=.05),
        sample_point='after_render_and_output_digest',warmup='same_renderer_K1_if_available_once',
        mde_t_critical_sums={'2':14.082586656645868,'20':2.9539746046772377},
        source_sha256={n:sha(HERE/n) for n in sorted(SOURCE_FILES)},
        usb_contract_sha256=sha(HERE/'usb_contract.json'),usb_contract=json.loads((HERE/'usb_contract.json').read_text()),
        protocol=dict(filename=PROTOCOL,sha256=sha(SIM/'prereg'/PROTOCOL)),
        reference_sha256={n:sha(HERE/n) for n in ('cache_manifest.json','cache_functional_audit.json','engineering_lock.json','usb_contract.json')},
        device_qa_verification_sha256=sha(qa/'final_verification.json'),
        weights_sha256=manifest['source_material_sha256']['yolov8n-seg.pt'],
        source_material_sha256=manifest['source_material_sha256'],
        original_material_lock_sha256=manifest['source_lock_sha256'],
        analysis=dict(unit='image',primary='adv_candidate_over_pooled_baseline',secondary='clean_descriptive',
            bootstrap_replicates=20000,seeds=dict(adv=2026111401,clean=2026111402,aa_clean=2026111403,aa_adv=2026111404),
            primary_two_sided_exact_signflip=True,one_confirmatory_endpoint=True),
        no_page_cache_flush=True,latency_endpoint_recorded=False)
    with (HERE/'memory_registration.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2)
    registration(HERE/'memory_registration.json',TAG,'0'*40)
    print('Scientific configuration created and validated; no tag/deployment/measurement performed.')


if __name__=='__main__':build()
