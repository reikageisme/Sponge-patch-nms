# A2. Một lớp so với 80 lớp ngẫu nhiên

## Lưới đã đo

| Số anchor | nc | Các giá trị N đã đo |
|---|---|---|
| 2100 | 1 | 0, 10, 30, 100, 300, 600, 1000, 1500, 2100 |
| 2100 | 80 | 0, 10, 30, 100, 300, 600, 1000, 1500, 2100 |
| 8400 | 80 | 0, 100, 300, 1000, 3000, 8400 |
| 10000 | 80 | 100, 300, 1000, 3000, 10000 |

## Ô có cả hai (không cap)

| Anchor | NMS | Hình học | N | nc = 80 (ms) | nc = 1 (ms) | nc1 / nc80 |
|---|---|---|---|---|---|---|
| 2100 | torch_pure | dense_cluster | 1000 | 1.091 | 1.026 | 0.94 |
| 2100 | torch_pure | dense_cluster | 1500 | 1.159 | 1.150 | 0.99 |
| 2100 | torch_pure | dense_cluster | 2100 | 1.312 | 1.267 | 0.96 |
| 2100 | torch_pure | disjoint | 1000 | 109.113 | 108.349 | 0.99 |
| 2100 | torch_pure | disjoint | 1500 | 170.483 | 170.882 | 1.00 |
| 2100 | torch_pure | disjoint | 2100 | 251.689 | 253.790 | 1.01 |
| 2100 | torch_pure | mixed | 1000 | 51.900 | 52.075 | 1.00 |
| 2100 | torch_pure | mixed | 1500 | 78.693 | 80.871 | 1.03 |
| 2100 | torch_pure | mixed | 2100 | 114.632 | 116.471 | 1.02 |
| 2100 | tv_batched | dense_cluster | 1000 | 0.925 | 0.233 | 0.25 |
| 2100 | tv_batched | dense_cluster | 1500 | 5.788 | 0.402 | 0.07 |
| 2100 | tv_batched | dense_cluster | 2100 | 6.340 | 0.492 | 0.08 |
| 2100 | tv_batched | disjoint | 1000 | 1.203 | 1.213 | 1.01 |
| 2100 | tv_batched | disjoint | 1500 | 6.024 | 2.818 | 0.47 |
| 2100 | tv_batched | disjoint | 2100 | 6.409 | 5.313 | 0.83 |
| 2100 | tv_batched | mixed | 1000 | 1.116 | 0.585 | 0.52 |
| 2100 | tv_batched | mixed | 1500 | 6.018 | 1.297 | 0.22 |
| 2100 | tv_batched | mixed | 2100 | 6.352 | 2.162 | 0.34 |
| 2100 | tv_nms | dense_cluster | 1000 | 0.221 | 0.184 | 0.83 |
| 2100 | tv_nms | dense_cluster | 1500 | 0.255 | 0.251 | 0.99 |
| 2100 | tv_nms | dense_cluster | 2100 | 0.358 | 0.323 | 0.90 |
| 2100 | tv_nms | disjoint | 1000 | 1.173 | 1.179 | 1.01 |
| 2100 | tv_nms | disjoint | 1500 | 2.430 | 2.454 | 1.01 |
| 2100 | tv_nms | disjoint | 2100 | 4.726 | 4.734 | 1.00 |
| 2100 | tv_nms | mixed | 1000 | 0.619 | 0.579 | 0.94 |
| 2100 | tv_nms | mixed | 1500 | 1.037 | 1.045 | 1.01 |
| 2100 | tv_nms | mixed | 2100 | 1.845 | 1.852 | 1.00 |
| 2100 | ultra_native | dense_cluster | 1000 | 1.479 | 0.522 | 0.35 |
| 2100 | ultra_native | dense_cluster | 1500 | 2.167 | 0.648 | 0.30 |
| 2100 | ultra_native | dense_cluster | 2100 | 3.206 | 0.755 | 0.24 |
| 2100 | ultra_native | disjoint | 1000 | 1.793 | 1.552 | 0.87 |
| 2100 | ultra_native | disjoint | 1500 | 3.222 | 2.867 | 0.89 |
| 2100 | ultra_native | disjoint | 2100 | 5.714 | 5.172 | 0.91 |
| 2100 | ultra_native | mixed | 1000 | 1.704 | 0.920 | 0.54 |
| 2100 | ultra_native | mixed | 1500 | 2.672 | 1.427 | 0.53 |
| 2100 | ultra_native | mixed | 2100 | 4.447 | 2.394 | 0.54 |

## Ô lớn nhất với nc = 80 (chỗ lời khuyên "class-batched" dựa vào)

| Anchor | NMS | Hình học | N | ms |
|---|---|---|---|---|
| 8400 | tv_batched | dense_cluster | 8400 | 9.65 |
| 8400 | tv_batched | disjoint | 8400 | 10.85 |
| 8400 | tv_batched | mixed | 8400 | 11.50 |
| 8400 | tv_nms | dense_cluster | 8400 | 1.31 |
| 8400 | tv_nms | disjoint | 8400 | 94.06 |
| 8400 | tv_nms | mixed | 8400 | 59.30 |
| 10000 | tv_batched | dense_cluster | 10000 | 9.88 |
| 10000 | tv_batched | disjoint | 10000 | 11.98 |
| 10000 | tv_batched | mixed | 10000 | 12.47 |
| 10000 | tv_nms | dense_cluster | 10000 | 1.54 |
| 10000 | tv_nms | disjoint | 10000 | 137.23 |
| 10000 | tv_nms | mixed | 10000 | 95.40 |

## Kết luận

- Ở lưới 2100 anchor, một lớp KHÔNG làm batched NMS đắt hơn; với hộp chồng nhau còn rẻ hơn (tỉ số dưới 1).
- Lợi thế lớn của `tv_batched` chỉ xuất hiện ở lưới lớn (8400, 10000 anchor), nơi torchvision chạy NMS riêng từng lớp khi có hơn 4000 hộp. Lưới này chưa có nc = 1: 8400, 10000.
- Cần đo bổ sung nc = 1 ở lưới lớn trước khi viết "class-batched kernel làm NMS không nhạy". Nếu một lớp xoá lợi thế đó thì lời khuyên phải ghi điều kiện "ứng viên trải trên nhiều lớp".

Lệnh gợi ý (cùng giao thức E1, chỉ thêm nc = 1 ở hai lưới lớn; đăng ký trước rồi mới chạy):

```bash
python sponge-sim/studies/e1_dose/run.py --run-dir sponge-sim/results/e1/E1_nc1_large --nc1-large
```
(cờ `--nc1-large` đã thêm vào `studies/e1_dose/run.py`: 36 nhóm, nc = 1 và nc = 80 ở 8400 và 10000 anchor, không cap.)