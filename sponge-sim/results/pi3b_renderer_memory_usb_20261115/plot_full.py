"""Plot all image units from independent raw replay; no filtering or device work."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B = Path(__file__).resolve().parent


def main():
    audit = json.loads((B/'independent_full_audit.json').read_text())
    table = audit['table']
    adv = [x for x in table if x['condition'] == 'adv']
    clean = [x for x in table if x['condition'] == 'clean']
    ids = [str(int(x['image'])) for x in adv]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.1), layout='constrained')
    for key, label, marker in [('pooled_baseline_bytes', 'Native 32M (median of 6)', 'o'),
                               ('candidate_bytes', 'Preallocated 16M (median of 3)', 's')]:
        axes[0].plot(ids, [x[key]/2**20 for x in adv], marker=marker, markersize=4, label=label)
    axes[0].set(ylabel='Whole-process high-water RSS (MiB)', title='Attacked caches: all 20 images')
    for rows, label, marker in [(adv, 'Attacked', 'o'), (clean, 'Clean (descriptive)', 's')]:
        axes[1].plot(ids, [x['candidate_over_baseline'] for x in rows], marker=marker, markersize=4, label=label)
    axes[1].axhline(1, color='gray', linestyle='--', linewidth=.8)
    axes[1].set(ylabel='Per-image candidate / pooled-native RSS', title='Same caches and exact output digests')
    for ax in axes:
        ax.set_xlabel('COCO image ID (frozen cohort order)')
        ax.tick_params(axis='x', rotation=65)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8, loc='best')
    fig.suptitle('Pi 3B / 600 MHz / 4 threads / idle SSD attached — RSS, not latency', fontsize=11)
    for suffix in ('png', 'pdf'):
        path = B/f'full_memory_per_image.{suffix}'
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path, dpi=180)
    plt.close(fig)


if __name__ == '__main__': main()
