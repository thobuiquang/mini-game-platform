/**
 * script.js - File JavaScript chính của Cổng Mini Game T36
 * ============================================================
 * Chức năng:
 *  1. Điều hướng trang (Trang chủ <-> Đăng nhập/Đăng ký)
 *  2. Chuyển đổi tab trên trang Login (Đăng nhập / Đăng ký)
 *  3. Xử lý validate form Đăng nhập và Đăng ký
 *  4. Xử lý click vào thẻ game (chuẩn bị tích hợp game)
 *  5. Tìm kiếm game theo tên
 *  6. Hiển thị thông báo Toast
 * ============================================================
 */

const API_BASE_URL = 'http://localhost:5000';
const BACKEND_TO_FRONTEND_GAME_NAME = {
  brick_breaker: 'brickbreaker'
};
let backendGames = new Set();

// ============================================================
// PHẦN 1: ĐIỀU HƯỚNG TRANG
// ============================================================

/**
 * Chuyển đến trang Đăng nhập (tab mặc định: Đăng nhập)
 * Được gọi khi nhấn nút "Đăng Nhập" trên Header của trang chủ
 */
function chuyenDenDangNhap() {
  // Lưu tab cần mở vào sessionStorage để login.html đọc
  sessionStorage.setItem('authTab', 'login');
  // Chuyển hướng sang trang đăng nhập
  window.location.href = 'login.html';
}

/**
 * Chuyển đến trang Đăng ký (tab mặc định: Đăng ký)
 * Được gọi khi nhấn nút "Đăng Ký" trên Header của trang chủ
 */
function chuyenDenDangKy() {
  // Lưu tab cần mở vào sessionStorage
  sessionStorage.setItem('authTab', 'register');
  // Chuyển hướng sang trang đăng nhập/đăng ký
  window.location.href = 'login.html';
}

/**
 * Quay về trang chủ
 */
function quayVeTrangChu() {
  window.location.href = 'index.html';
}

// ============================================================
// PHẦN 2: CHUYỂN ĐỔI TAB TRÊN TRANG ĐĂNG NHẬP / ĐĂNG KÝ
// ============================================================

/**
 * Chuyển đổi giữa 2 tab: 'login' và 'register'
 * @param {string} tabName - Tên tab cần hiển thị ('login' hoặc 'register')
 */
function chuyenTab(tabName) {
  // Lấy các phần tử DOM cần thao tác
  const tabLogin     = document.getElementById('tab-login');
  const tabRegister  = document.getElementById('tab-register');
  const panelLogin   = document.getElementById('panel-login');
  const panelRegister = document.getElementById('panel-register');

  // Kiểm tra xem đang ở trang login.html không
  if (!tabLogin || !panelLogin) return;

  if (tabName === 'login') {
    // --- Kích hoạt tab Đăng nhập ---
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    tabLogin.setAttribute('aria-selected', 'true');
    tabRegister.setAttribute('aria-selected', 'false');

    // Hiện panel Đăng nhập, ẩn panel Đăng ký
    panelLogin.style.display   = 'flex';
    panelRegister.style.display = 'none';

    // Thêm lại animation để panel "nảy" ra
    panelLogin.style.animation = 'none';
    void panelLogin.offsetHeight; // Trigger reflow để reset animation
    panelLogin.style.animation = 'fadeInUp 0.4s ease';

  } else if (tabName === 'register') {
    // --- Kích hoạt tab Đăng ký ---
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    tabRegister.setAttribute('aria-selected', 'true');
    tabLogin.setAttribute('aria-selected', 'false');

    // Hiện panel Đăng ký, ẩn panel Đăng nhập
    panelRegister.style.display = 'flex';
    panelLogin.style.display    = 'none';

    // Thêm lại animation
    panelRegister.style.animation = 'none';
    void panelRegister.offsetHeight;
    panelRegister.style.animation = 'fadeInUp 0.4s ease';
  }
}

// ============================================================
// PHẦN 3: XỬ LÝ FORM ĐĂNG NHẬP
// ============================================================

/**
 * Xử lý sự kiện Submit form Đăng nhập
 * Hiện tại chỉ validate input, chưa kết nối Backend
 * @param {Event} event - Sự kiện submit của form
 */
function xuLyDangNhap(event) {
  // Ngăn form tải lại trang (hành vi mặc định của HTML)
  event.preventDefault();

  // Lấy giá trị từ các input
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value.trim();

  // Biến theo dõi trạng thái hợp lệ
  let hopLe = true;

  // Xóa tất cả lỗi cũ trước khi validate lại
  xoaLoi('error-login-username');
  xoaLoi('error-login-password');

  // Kiểm tra tên đăng nhập không được rỗng
  if (!username) {
    hienLoi('error-login-username', 'Vui lòng nhập tên đăng nhập!');
    hopLe = false;
  }

  // Kiểm tra mật khẩu không được rỗng
  if (!password) {
    hienLoi('error-login-password', 'Vui lòng nhập mật khẩu!');
    hopLe = false;
  }

  // Nếu không hợp lệ, dừng lại
  if (!hopLe) return;

  // TODO: Gọi API Backend để xác thực thông tin đăng nhập
  // Hiện tại: Giả lập đăng nhập thành công và chuyển về trang chủ
  hienToast('✅ Đăng nhập thành công! Chào mừng ' + username + '!', 'success');

  // Lưu tên đăng nhập vào sessionStorage để trang chủ đọc lại
  sessionStorage.setItem('loggedUser', username);

  // Chuyển về trang chủ sau 1.5 giây
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 1500);
}

// ============================================================
// PHẦN 4: XỬ LÝ FORM ĐĂNG KÝ
// ============================================================

/**
 * Xử lý sự kiện Submit form Đăng ký
 * Validate đầy đủ: tên, mật khẩu, xác nhận mật khẩu
 * @param {Event} event - Sự kiện submit của form
 */
function xuLyDangKy(event) {
  // Ngăn form tải lại trang
  event.preventDefault();

  // Lấy giá trị từ các input
  const username        = document.getElementById('reg-username').value.trim();
  const password        = document.getElementById('reg-password').value;
  const confirmPassword = document.getElementById('reg-confirm-password').value;

  // Biến theo dõi trạng thái hợp lệ
  let hopLe = true;

  // Xóa tất cả lỗi cũ
  xoaLoi('error-reg-username');
  xoaLoi('error-reg-password');
  xoaLoi('error-reg-confirm');

  // Kiểm tra tên đăng nhập
  if (!username) {
    hienLoi('error-reg-username', 'Vui lòng nhập tên đăng nhập!');
    hopLe = false;
  } else if (username.length < 3) {
    hienLoi('error-reg-username', 'Tên đăng nhập phải có ít nhất 3 ký tự!');
    hopLe = false;
  }

  // Kiểm tra mật khẩu: độ dài tối thiểu 6 ký tự
  if (!password) {
    hienLoi('error-reg-password', 'Vui lòng nhập mật khẩu!');
    hopLe = false;
  } else if (password.length < 6) {
    hienLoi('error-reg-password', 'Mật khẩu phải có ít nhất 6 ký tự!');
    hopLe = false;
  }

  // Kiểm tra mật khẩu xác nhận có khớp không
  if (!confirmPassword) {
    hienLoi('error-reg-confirm', 'Vui lòng xác nhận mật khẩu!');
    hopLe = false;
  } else if (password !== confirmPassword) {
    hienLoi('error-reg-confirm', 'Mật khẩu xác nhận không khớp!');
    hopLe = false;
  }

  // Nếu không hợp lệ, dừng lại
  if (!hopLe) return;

  // TODO: Gọi API Backend để tạo tài khoản mới
  // Hiện tại: Giả lập đăng ký thành công
  hienToast('🎉 Đăng ký thành công! Hãy đăng nhập để chơi game!', 'success');

  // Sau 1.5 giây, tự chuyển sang tab Đăng nhập
  setTimeout(() => {
    chuyenTab('login');
    // Điền sẵn tên đăng nhập vào form đăng nhập
    const loginInput = document.getElementById('login-username');
    if (loginInput) loginInput.value = username;
  }, 1500);
}

// ============================================================
// PHẦN 5: XỬ LÝ CLICK VÀO THẺ GAME
// ============================================================

/**
 * Ánh xạ tên game sang đường dẫn file game
 * Khi tích hợp game thật, thêm đường dẫn vào đây
 */
const GAME_ROUTES = {
  'snake':        'games/snake.html',       // Game Rắn săn mồi
  'tetris':       'games/tetris.html',      // Game Xếp gạch
  'caro':         'games/caro.html',        // Game Caro
  'flappy':       'games/flappy.html',      // Game Flappy Bird
  'brickbreaker': 'games/brickbreaker.html' // Game Phá gạch
};

function chuyenTenGameBackendSangFrontend(tenGameBackend) {
  return BACKEND_TO_FRONTEND_GAME_NAME[tenGameBackend] || tenGameBackend;
}

async function taiDanhSachGameTuBackend() {
  try {
    const response = await fetch(API_BASE_URL + '/api/games');
    if (!response.ok) {
      throw new Error('Backend response error: ' + response.status);
    }
    const payload = await response.json();
    if (!payload.success || !Array.isArray(payload.data)) {
      throw new Error('Invalid games payload');
    }

    backendGames = new Set(payload.data.map((game) => chuyenTenGameBackendSangFrontend(game.name)));
    return true;
  } catch (_error) {
    backendGames = new Set();
    return false;
  }
}

/**
 * Gắn sự kiện click cho tất cả các thẻ game trên lưới
 * Được gọi khi trang chủ (index.html) tải xong
 */
function khoiTaoLuoiGame() {
  // Lấy tất cả thẻ game trong lưới
  const tatCaTheGame = document.querySelectorAll('.game-card');

  tatCaTheGame.forEach(function(theGame) {
    theGame.addEventListener('click', function(event) {
      // Lấy loại game từ thuộc tính data-game
      const loaiGame = this.dataset.game;

      // Xử lý theo loại game
      if (loaiGame === 'coming-soon') {
        // Game chưa có - hiển thị thông báo
        event.preventDefault();
        hienToast('🔒 Game này sắp ra mắt! Hãy theo dõi T36 nhé!');
      } else if (backendGames.size > 0 && !backendGames.has(loaiGame)) {
        event.preventDefault();
        hienToast('⚠️ Backend chưa bật game này, vui lòng thử lại sau!');

      } else if (GAME_ROUTES[loaiGame]) {
        // Game đã có đường dẫn - chuyển đến trang game
        event.preventDefault();
        hienToast('🎮 Đang tải game ' + this.querySelector('.game-card__name').textContent + '...');
        setTimeout(() => {
          window.location.href = GAME_ROUTES[loaiGame];
        }, 800);

      }
      // Nếu là thẻ <a> có href thật, để trình duyệt xử lý mặc định
    });
  });
}

// ============================================================
// PHẦN 6: CHỨC NĂNG TÌM KIẾM GAME
// ============================================================

/**
 * Lọc và hiển thị game theo từ khóa tìm kiếm
 * Ẩn các thẻ game không khớp với từ khóa
 * @param {string} tuKhoa - Từ khóa người dùng nhập vào
 */
function timKiemGame(tuKhoa) {
  // Chuẩn hóa từ khóa: loại bỏ khoảng trắng, chuyển sang chữ thường
  const tuKhoaChuan = tuKhoa.trim().toLowerCase();

  // Lấy tất cả thẻ game
  const tatCaTheGame = document.querySelectorAll('.game-card');

  // Biến đếm số game tìm thấy
  let soGameTimThay = 0;

  tatCaTheGame.forEach(function(theGame) {
    // Lấy tên game từ phần tử .game-card__name
    const tenGame = theGame.querySelector('.game-card__name');
    if (!tenGame) return;

    const tenGameText = tenGame.textContent.toLowerCase();

    if (tuKhoaChuan === '' || tenGameText.includes(tuKhoaChuan)) {
      // Hiện thẻ game nếu từ khóa rỗng hoặc tên chứa từ khóa
      theGame.style.display = '';
      soGameTimThay++;
    } else {
      // Ẩn thẻ game không khớp
      theGame.style.display = 'none';
    }
  });

  // Thông báo kết quả tìm kiếm nếu có từ khóa
  if (tuKhoaChuan && soGameTimThay === 0) {
    hienToast('🔍 Không tìm thấy game "' + tuKhoa + '"!');
  }
}

// ============================================================
// PHẦN 7: TIỆN ÍCH - Hiển thị/Ẩn lỗi & Toast
// ============================================================

/**
 * Hiển thị thông báo lỗi bên dưới trường input
 * @param {string} idLoi - ID của phần tử hiển thị lỗi
 * @param {string} noiDung - Nội dung thông báo lỗi
 */
function hienLoi(idLoi, noiDung) {
  const phanTuLoi = document.getElementById(idLoi);
  if (!phanTuLoi) return;
  phanTuLoi.textContent = noiDung;
  phanTuLoi.classList.add('show');
}

/**
 * Ẩn thông báo lỗi
 * @param {string} idLoi - ID của phần tử chứa lỗi cần ẩn
 */
function xoaLoi(idLoi) {
  const phanTuLoi = document.getElementById(idLoi);
  if (!phanTuLoi) return;
  phanTuLoi.classList.remove('show');
}

/**
 * Hiển thị thông báo Toast nổi ở góc dưới phải màn hình
 * @param {string} noiDung - Nội dung thông báo cần hiển thị
 */
function hienToast(noiDung) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  // Cập nhật nội dung và hiển thị
  toast.textContent = noiDung;
  toast.classList.add('show');

  // Tự ẩn sau 3 giây
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// ============================================================
// PHẦN 8: CẬP NHẬT HEADER KHI ĐÃ ĐĂNG NHẬP
// ============================================================

/**
 * Kiểm tra sessionStorage xem người dùng đã đăng nhập chưa.
 * Nếu có: ẩn nút ĐN/ĐK, hiện avatar + tên ở góc phải header.
 */
function capNhatHeaderNguoiDung() {
  const tenDangNhap = sessionStorage.getItem('loggedUser');

  const btnLogin    = document.getElementById('btn-header-login');
  const btnRegister = document.getElementById('btn-header-register');
  const userInfo    = document.getElementById('user-info');
  const userAvatar  = document.getElementById('user-avatar');
  const userName    = document.getElementById('user-display-name');

  // Chỉ chạy nếu các phần tử tồn tại (trang chủ)
  if (!btnLogin || !userInfo) return;

  if (tenDangNhap) {
    // Ẩn nút Đăng nhập và Đăng ký
    btnLogin.style.display    = 'none';
    btnRegister.style.display = 'none';

    // Hiện khối user-info
    userInfo.style.display = 'flex';

    // Đặt chữ đại diện (ký tự đầu tiên của tên) làm nội dung avatar
    userAvatar.textContent = tenDangNhap.charAt(0).toUpperCase();

    // Hiển thị tên đăng nhập bên dưới
    userName.textContent = tenDangNhap;
  }
}

// ============================================================
// PHẦN 9: KHỞI ĐỘNG KHI TRANG TẢI XONG
// ============================================================

/**
 * Hàm chính - chạy ngay khi DOM sẵn sàng
 * Kiểm tra đang ở trang nào để khởi tạo đúng chức năng
 */
document.addEventListener('DOMContentLoaded', async function () {

  // ----- Xác định trang hiện tại -----
  const trangHienTai = window.location.pathname;
  const laTrangChu   = trangHienTai.includes('index.html') || trangHienTai.endsWith('/') || trangHienTai === '';
  const laTrangAuth  = trangHienTai.includes('login.html');

  // ===== KHỞI TẠO CHO TRANG CHỦ (index.html) =====
  if (laTrangChu || !laTrangAuth) {
    const daKetNoiBackend = await taiDanhSachGameTuBackend();
    if (!daKetNoiBackend) {
      hienToast('⚠️ Chưa kết nối được backend tại ' + API_BASE_URL);
    }

    // Cập nhật header nếu người dùng đã đăng nhập (ẩn nút ĐN/ĐK, hiện avatar)
    capNhatHeaderNguoiDung();

    // Gắn sự kiện click cho các thẻ game
    khoiTaoLuoiGame();

    // Gắn sự kiện tìm kiếm vào thanh search bar
    const oTimKiem = document.getElementById('search-input');
    if (oTimKiem) {
      // Tìm kiếm realtime khi người dùng gõ
      oTimKiem.addEventListener('input', function () {
        timKiemGame(this.value);
      });

      // Gửi tìm kiếm khi nhấn Enter
      oTimKiem.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          timKiemGame(this.value);
        }
      });
    }
  }

  // ===== KHỞI TẠO CHO TRANG ĐĂNG NHẬP (login.html) =====
  if (laTrangAuth) {
    // Đọc tab cần mở từ sessionStorage (được ghi khi click từ trang chủ)
    const tabCanMo = sessionStorage.getItem('authTab');

    if (tabCanMo === 'register') {
      // Mở tab Đăng ký nếu người dùng nhấn "Đăng Ký" từ trang chủ
      chuyenTab('register');
    } else {
      // Mặc định mở tab Đăng nhập
      chuyenTab('login');
    }

    // Xóa dữ liệu session sau khi đã đọc (dọn dẹp)
    sessionStorage.removeItem('authTab');
  }

  // ----- Thêm hiệu ứng "phát sáng" khi hover sidebar badge -----
  const sidebarBadge = document.getElementById('btn-category');
  if (sidebarBadge) {
    sidebarBadge.addEventListener('click', function () {
      hienToast('🗂️ Tính năng lọc theo thể loại đang được phát triển!');
    });
  }

  // Thông báo chào mừng khi vào trang chủ
  if (laTrangChu) {
    setTimeout(() => {
      hienToast('🎮 Chào mừng đến với T36 Mini Game Portal!');
    }, 600);
  }
});
