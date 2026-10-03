# VinFast eBus US — static cut

HTML/CSS/JS tĩnh cắt từ Figma **34. EBus** (`FyAlNr7utu468hKIcfAWqh`), Desktop 1440 + Mobile 390.

| Trang | File | Figma Desktop | Figma Mobile |
|---|---|---|---|
| Homepage | `home/index.html` | `2120:3717` | `2120:4210` |
| About Us | `about-us/index.html` | `2120:3813` | `2120:4316` |
| Our Buses | `our-buses/index.html` | `2120:3939` | `2120:4461` (Figma đặt nhầm tên "About-us_Mobile") |
| Contact Us | `contact-us/index.html` | `2120:4621` | `2120:4655` |

## Cấu trúc

Chỉ HTML + CSS + JS thuần, không cần Node hay bước build nào.

```
home/          index.html + style.css   (Homepage)
about-us/      index.html + style.css
our-buses/     index.html + style.css
contact-us/    index.html + style.css
assets/
  images/      ảnh WebP đã nén từ Figma
  fonts/       Mulish (woff2, self-host)
  icons/       logo đối tác (SVG)
  js/main.js   JS dùng chung: menu mobile, slider, carousel, tab EB12/EB8
```

- Mỗi `style.css` đứng độc lập: phần chung (font, base, nút, header, footer) được lặp lại
  trong từng file, phần riêng chỉ có ở trang dùng nó. Sửa header/footer thì sửa ở cả 4 file.
- Icon 1 màu được nhúng thẳng trong CSS (data URI, đổi màu theo `color`).
- Mở trực tiếp file `home/index.html` trong trình duyệt là xem được; hoặc chạy server tĩnh bất kỳ
  (VD `python3 -m http.server` tại thư mục này rồi vào `/home/index.html`).

Breakpoint: mobile-first, chuyển layout desktop ở `1024px`.
Lề trang (biến CSS `--pad` / `--pad-wide` / `--pad-specs` trong `:root`): từ 1440px trở lên giữ đúng
padding Figma 185 / 75 / 155px, nội dung giãn theo màn hình; trên 1920px nội dung ngừng giãn và được
căn giữa. Dưới 1440px lề co dần về 40px (tablet) / 16px (mobile).

Ảnh có crop riêng trong Figma dùng class `fig-crop` + biến `--cw/--ch/--cx/--cy` (và `*-lg` cho desktop)
lấy từ `imageTransform` của Figma.

## Hook JS (data-attribute)

- **Carousel scroll-snap**: `data-carousel` (+ `data-carousel-start="n"`), `data-carousel-track`,
  `data-carousel-prev` / `-next` / `-dots`. Kéo được bằng chuột trên desktop.
- **Fade slider**: `data-fader` (+ `data-fade-loop`), `data-fade-slide="n"` trên mọi phần tử thuộc
  slide n (text và ảnh có thể nằm ở 2 chỗ khác nhau), `data-fade-prev` / `-next` / `-dots`.
- **Tab EB12/EB8**: `data-model-switch` + `data-model-tab="eb12|eb8"` + `data-model="eb12|eb8"`.
- **Menu mobile**: `data-header` + `data-header-toggle`.

Dots chỉ hiện khi có từ 2 slide trở lên.

## Khác với Figma (có chủ ý)

Đã đối chiếu tự động từng text (cỡ chữ, line-height, độ đậm, màu, vị trí) và kích thước
các khối ở 1440px và 390px. Những điểm còn khác đều là chủ ý:

- Our Buses: bỏ thanh sub-nav thứ 2 (theo yêu cầu) → trang ngắn hơn ~300px.
- Bảng spec Our Buses: nhãn và giá trị thẳng hàng theo từng dòng (Figma lệch nhau 23px);
  ô giá trị padding ngang 8px để "90 (35 Seating + 1 Wheelchair + 54 Standing)" nằm trên 1 dòng.
- Card sản phẩm mobile: dòng quá dài ("2 x 325 kW … Dual Hub Motors") xuống dòng thay vì
  bị cắt như Figma; khoảng cách nhãn–giá trị 6px (Figma 8px) để các dòng khác vẫn vừa 1 dòng.
- Logo đối tác mobile thu 85% để vừa 1 hàng (Figma tràn ra ngoài màn hình).
- About mobile: timeline dùng nội dung bản Desktop (bản Mobile còn năm 2025 + text placeholder).
- Không hiện chấm phân trang khi chỉ có 1 ảnh (Smart Tech, Why choose, hero Homepage mobile).

## Nội dung cần xác nhận (TODO)

- Our Buses: hero slide EB8 (chưa có trong Figma, đang lấy số từ bảng spec + Homepage);
  card Exterior "Entrance" là text placeholder; Front Light / Rear View / Top View chưa có mô tả;
  nút xoay 360° mới là UI.
- About: link "Our company profile" (video hay PDF?), icon Play đang bị ẩn trong Figma.
- Link Terms / Privacy / Cookies / LinkedIn / Download Brochure / Download Specifications đang để `#`.
