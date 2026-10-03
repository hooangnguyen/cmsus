# VinFast eBus — bản cắt cho CMS

Cắt theo chuẩn trang **VF Wild** (node 11846 trên stg-cms-v2): mỗi trang là 1 node,
nội dung chia vào các field của CMS, **không có header/footer** (CMS tự render).

```
cms/
  src/<page>/      content.html + style.css, src/ebus.js   → nguồn, chỉ sửa ở đây
  <page>/          body.html + style.css                    → sinh bởi build.py
  dist/<page>.html → style + markup + script gộp 1 file (dán vào Body)
  cdn/ebus-2026/   → ảnh + logo đối tác (đã upload lên CDN)
  build.py         → sinh <page>/, dist/, preview/
```

Mỗi `<page>/` gồm:
- `body.html`: markup (`<div id="vf-ebus-scope">…</div>`) + `<script>` (slider, carousel, tab EB12/EB8) ở cuối file; dòng đầu `<link>` nạp `style.css` cùng thư mục.
- `style.css`: CSS của trang, tự nạp font Mulish bằng `@import`.

## Dán vào CMS

| File | Field CMS | Ghi chú |
|---|---|---|
| `<page>/body.html` | **Body**, định dạng `Master HTML` | Bọc trong `<div id="vf-ebus-scope">` |
| `<page>/style.css` | **Custom Style** | Bọc trong `<style>…</style>` nếu field cần HTML |
| `src/ebus.js` | Theme JS (dev tích hợp) | Giống VF Wild: JS nằm trong theme. Hoặc nhúng `<script src=".../ebus.js" defer>` nếu CMS cho phép |

`ebus.js` dùng chung cho cả 4 trang, không cần jQuery. Script tự thoát nếu trang không có
`#vf-ebus-scope`, và chạy được cả khi được load sau `DOMContentLoaded`.

## Chống bị theme override

- Mọi selector đều bắt đầu bằng `#vf-ebus-scope`, nên specificity có ID và thắng các rule
  của Bootstrap 4/theme. Style trang này cũng không lọt ra ngoài.
- Mọi class đều có prefix `vfe-` (`vfe-btn`, `vfe-container`, `vfe-icon`…), nên không trùng
  `.btn` / `.container` / `.card` của Bootstrap. State class giữ là `is-active` (giống VF Wild).
- Hook JS là `data-vfe-*` (`data-vfe-carousel`, `data-vfe-fader`, `data-vfe-model-tab`…), id có prefix `vfe-`.
- Đầu mỗi file style có block **CMS guard**: reset font-family, size, màu và margin của
  `h1–h6`, `p`, `li`, `sup`… mà theme có thể đặt sẵn.
- Biến CSS (`--pad`…) khai báo trên `#vf-ebus-scope`, không đặt trên `:root`.

Đã kiểm tra: khi nạp Bootstrap 4.6 trước style của trang, layout trùng khớp với bản cắt gốc
(đo vị trí, kích thước, font, màu của từng phần tử ở 1440px và 390px).

## CDN

Mọi link asset đang trỏ về `https://static-cms-prod.vinfastauto.us/statics/ebus-2026/` (đặt
theo cách VF Wild dùng `statics/wild-2026/`). Upload phẳng toàn bộ `cdn/ebus-2026/` lên đó.
Nếu đường dẫn thật khác thì find & replace chuỗi trên trong `src/`, rồi chạy lại `build.py`.

Icon 1 màu (mũi tên, logo EB12/EB8, icon USP) vẫn nhúng dạng data URI trong CSS. Lý do:
chúng dùng `mask-image`, mà mask từ domain khác cần CDN trả header CORS. Nếu không có header
này thì icon sẽ mất.

## Link nội bộ (tạm, cập nhật sau)

`/ebus`, `/ebus/about-us`, `/ebus/our-buses`, `/ebus/contact-us`. Các link Terms, Brochure,
Specifications… vẫn để `#`.

## Đối chiếu Figma

Đã so ảnh chụp từng frame Figma với bản render ở 1440px và 390px. Ngoài các điểm dưới đây,
vị trí, cỡ chữ và màu đều khớp. Card sản phẩm Home cao đúng 474px như Figma.

Các điểm khác Figma có chủ ý:
- Our Buses: bỏ thanh sub-nav (Overview / External / Internal / Tech / Specs) theo yêu cầu,
  nên trang ngắn hơn khoảng 300px.
- Bảng spec Our Buses: nhãn và giá trị thẳng hàng theo từng dòng (Figma lệch nhau 23px).
- Card sản phẩm mobile: dòng "2 x 325 kW … Dual Hub Motors" xuống dòng, thay vì bị cắt như Figma.
- Logo đối tác mobile thu nhỏ 85% để vừa 1 hàng.
- About mobile: timeline dùng nội dung bản Desktop (bản Mobile còn năm 2025 và text placeholder).
- Không hiện chấm phân trang khi chỉ có 1 ảnh (Smart Tech, Why choose, hero Homepage mobile).

## Xem thử local

```
python3 build.py                   # sinh <page>/, dist/, preview/
```

Mở `preview/<page>.html` để xem thử (Bootstrap 4 nạp trước, giả lập theme). Ảnh tải thẳng từ CDN.
Sửa nội dung thì sửa trong `src/`, rồi chạy lại `build.py`.
