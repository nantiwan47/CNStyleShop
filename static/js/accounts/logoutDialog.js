<!-- JavaScript สำหรับควบคุมการแสดง/ซ่อนกล่องไดอะล็อก -->
const logoutBtn = document.getElementById('logoutBtn');
const logoutDialog = document.getElementById('logoutDialog');
const cancelBtn = document.getElementById('cancelBtn');

// ตรวจสอบการมีอยู่ของปุ่มก่อนที่จะเพิ่ม event listener
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        logoutDialog.classList.remove('hidden');
    });
}

if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
        logoutDialog.classList.add('hidden');
    });
}
