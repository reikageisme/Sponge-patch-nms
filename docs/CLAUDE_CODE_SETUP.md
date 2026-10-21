# Bộ khởi động Claude Code cho đề tài Sponge Patch

> Chuyển từ `README.md` gốc (bản starter-kit chưa commit) ngày 21/10/2026 theo yêu cầu nhóm; nội dung giữ nguyên.

## Cài đặt (1 phút)
1. Giải nén vào GỐC repo `D:\Physical-Visual-DoS-EdgeAI-main`, sao cho có:
   - `CLAUDE.md`
   - `.claude/settings.json`
   - `.claude/skills/sponge-research/SKILL.md`
   - `docs/PROMPT_STEP1.md`
2. Nếu repo đã có `CLAUDE.md` hoặc `.claude/settings.json`: ĐỪNG ghi đè, hãy gộp tay.
3. Mở terminal ở gốc repo, chạy `claude`.
4. Gõ `/permissions` để kiểm tra quy tắc allow/deny đã nạp đúng; gõ `/skills` (hoặc hỏi "có skill nào?") để thấy `sponge-research`.

## Tin nhắn mở đầu (dán vào Claude Code)
```
Đọc CLAUDE.md, REVIEW/03*.md, REVIEW/04*.md và docs/PROMPT_STEP1.md.
Vào plan mode, đề xuất kế hoạch cho Bước 1 (E1, E2, E5) rồi chờ tôi duyệt.
Dùng skill sponge-research. Tạo nhánh harness/step1. Chưa viết code trước khi tôi duyệt.
```

## Tiết kiệm token
- Hết một giai đoạn: `/clear`, rồi mở phiên mới bằng "Đọc CLAUDE.md và sponge-sim/PROGRESS.md, làm tiếp".
- Phiên dài nhưng chưa muốn bỏ: `/compact`.
- Quay lại phiên cũ: `claude --continue` (phiên gần nhất) hoặc `claude --resume`.
- Yêu cầu Claude chạy việc dài ở nền, ghi log, chỉ đọc đuôi log.
- Commit nhỏ; mọi tiến độ nằm ở `PROGRESS.md`, không nằm trong đầu phiên chat.
